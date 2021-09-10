#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import threading

def recvall(sock, delim):
	data = b""
	while True:
		more = sock.recv(1)
		
		if more == delim:
			break
		data += more
	return data

def toCSV(msg):
	csv = ""
	for l in msg:
		csv += ",".join(l) + "\n"
	return csv

def fromCSV(msg):
	dados = []
	for l in msg.splitlines():
		ele = l.split(",")
		dados.append(ele)
	return dados

class Atendimento(threading.Thread):
	
	trava = threading.Lock()
	emails = {}
	
	def __init__(self,sc):
		super().__init__()
		self.sc = sc
		
	def validar(self, msg):
		Atendimento.trava.acquire()
		if msg[1] in Atendimento.emails:
			t_email = 0
			
			for e in Atendimento.emails[msg[1]]:
				if e[3] == "NOVA":
					t_email += 1
			self.sc.sendall("Você tem {} mensagens não lidas\n".format(t_email).encode())
			
		else:
			self.sc.sendall("Usuário não registrado no PyMessenger\n".encode())
		Atendimento.trava.release()
			
	
	def registrar(self, msg):
		Atendimento.trava.acquire()
		if msg[1] in Atendimento.emails:
			self.sc.sendall("O usuário {} já está registrado no Servidor!\n".format(msg[1]).encode())
		else:
			Atendimento.emails[msg[1]] = []
			self.sc.sendall("Usuário {} registrado com sucesso!\n".format(msg[1]).encode())
		Atendimento.trava.release()
		
		
	def enviar_mensagem(self, msg):
		Atendimento.trava.acquire()
		try:
			Atendimento.emails[msg[2]].append([msg[1],msg[3],msg[4],"NOVA"])
		except KeyError:
			self.sc.sendall("Usuário de destino não registrado!\n".encode())
		else:
			self.sc.sendall("Email enviado com sucesso!\n".encode())
		Atendimento.trava.release()
	
	def listar_mensagens(self, msg):
		assuntos = ["OK"]
		Atendimento.trava.acquire()
		try:
			for email in Atendimento.emails[msg[1]]:
				assuntos.append(email[1] + ("*" if email[3] == "NOVA" else ""))
		except KeyError:
			self.sc.sendall(toCSV([["NR"]]).encode())
		else:
			self.sc.sendall(toCSV([assuntos]).encode())
		Atendimento.trava.release()
	
	def ler_mensagem(self, msg):
		Atendimento.trava.acquire()
		Atendimento.emails[msg[1]][int(msg[2])-1][3] = "LIDA"
		self.sc.sendall(toCSV([Atendimento.emails[msg[1]][int(msg[2])-1]]).encode())
		Atendimento.trava.release()
	
	def apagar_mensagem(self, msg):
		Atendimento.trava.acquire()
		Atendimento.emails[msg[1]].pop(int(msg[2])-1)
		Atendimento.trava.release()
		self.sc.sendall(b"Mensagem apagada com sucesso.\n")
		
	
	def run(self):
		print("Atendendo Cliente",self.sc.getpeername())
	
		msg = fromCSV(recvall(self.sc,b"\n").decode())[0]
		
		while msg[0] != "SAIR":
			{"VALIDAR":self.validar,
			 "REGISTRAR":self.registrar,
			 "ENVIARMSG":self.enviar_mensagem,
			 "LISTARMSGS":self.listar_mensagens,
			 "LERMSG":self.ler_mensagem,
			 "APAGARMSG":self.apagar_mensagem
			 }[msg[0]](msg)
			
			msg = fromCSV(recvall(self.sc,b"\n").decode())[0]
		
		self.sc.sendall(b"Desconectado.\n")
		self.sc.close()

def main():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(('127.0.0.1',50000))
	sock.listen(5)
	
	print("Ouvindo em", sock.getsockname())
	
	MAX_THREADS = 8
	l_threads = []
	
	while True:
		sc, sockname = sock.accept()
		
		l_threads.append(Atendimento(sc))
		l_threads[-1].start()
		
		while len(l_threads) >= MAX_THREADS:
			l_threads = [t for t in l_threads if t.is_alive()]
		
	return 0

if __name__ == '__main__':
    main()
