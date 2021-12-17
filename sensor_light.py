import serial
from datetime import datetime
from serial.tools import list_ports

# lista as portas do arduino
conexao = ""
for port in list_ports.comports():
  print('Dispositivo: {} - porta: {} '.format(port.description, port.device))
  if "USB" in str(port.description.upper()):
    try:
      conexao = serial.Serial(port.device, 115200)
      print('Conexão realizada com sucesso {}.'.format(conexao.portstr))
    except:
      pass

if conexao != "":
  while True:
    resposta = conexao.readline()
    print(datetime.now(), float(resposta.decode()))
  conexao.close()
