#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import os, sys

def recvall(sock, delim):
	data = b""
	while True:
		more = sock.recv(1)
		
		if more == delim:
			break
		data += more
	return data

def fromCSV(msg):
	dados = []
	for l in msg.splitlines():
		ele = l.split(",")
		dados.append(ele)
	return dados

def menu():
	os.system("cls")
	print("""PyMessenger
 [1] Registrar
 [2] Enviar Mensagem
 [3] Ler Mensagens
 [4] Apagar Mensagens
 [5] Sair
""")
	return input("Op: ")

def registrar(sock, user):
	sock.sendall("REGISTRAR,{}\n".format(user).encode())
	print(recvall(sock,b"\n").decode())
	input("Tecle ENTER para continuar...")

def enviar_mensagem(sock, user):
	print("MENSAGEM:")
	d = input("Destinatário: ")
	a = input("Assunto: ")
	m = input("Mensagem: ")
	sock.sendall("ENVIARMSG,{},{},{},{}\n".format(user,d,a,m).encode())
	print(recvall(sock,b"\n").decode())
	input("Tecle ENTER para continuar...")

def ler_mensagens(sock, user):
	sock.sendall("LISTARMSGS,{}\n".format(user).encode())
	dados = fromCSV(recvall(sock,b"\n").decode())[0]
	
	if dados[0] == "NR":
		print("Usuário não registrado")
	elif len(dados) > 1:
		c = 1
		for msg in dados[1:]:
			if msg[-1] == "*":
				print("{}. {} - NOVA".format(c,msg[:-1]))
			else:
				print("{}. {}".format(c,msg))
			c+=1
		op = input("Ler mensagem > ")
		sock.sendall("LERMSG,{},{}\n".format(user,op).encode())
		dados = fromCSV(recvall(sock,b"\n").decode())[0]
		print("REMENTENTE:",dados[0])
		print("ASSUNTO:",dados[1])
		print("MENSAGEM:",dados[2])
	else:
		print("Nenhuma mensagem.")
	input("Tecle ENTER para continuar...")

def apagar_mensagens(sock, user):
	sock.sendall("LISTARMSGS,{}\n".format(user).encode())
	dados = fromCSV(recvall(sock,b"\n").decode())[0]
	
	tem_para_apagar = False
	
	if dados[0] == "NR":
		print("Usuário não registrado")
	elif len(dados) > 1:
		c = 1
		for msg in dados[1:]:
			if msg[-1] == "*":
				pass
			else:
				print("{}. {}".format(c,msg))
				tem_para_apagar = True
			c+=1
		if tem_para_apagar:
			op = input("Apagar mensagem > ")
			sock.sendall("APAGARMSG,{},{}\n".format(user,op).encode())
			print(recvall(sock,b"\n").decode())
		else:
			print("Nenhuma mensagem.")
	else:
		print("Nenhuma mensagem.")
	input("Tecle ENTER para continuar...")
	
def sair(sock, user):
	sock.sendall("SAIR,{}\n".format(user).encode())
	print(recvall(sock,b"\n").decode())
	sock.close()
	sys.exit(0)
	

def main():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(('127.0.0.1',50000))
	
	print("Bem-vindo ao PyMessenger!")
	user = input("Entre com o nome de usuário: ")
	
	sock.sendall("VALIDAR,{}\n".format(user).encode())
	print(recvall(sock,b"\n").decode())
	input("Tecle ENTER para continuar...")
	
	while True:
		op = menu()
		{"1":registrar,
		 "2":enviar_mensagem,
		 "3":ler_mensagens,
		 "4":apagar_mensagens,
		 "5":sair}[op](sock,user)

	return 0

if __name__ == '__main__':
    main()
