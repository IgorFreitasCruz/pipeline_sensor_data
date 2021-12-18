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

def get_sensor():
  """If there is a connection returnes sensor data."""
  if conexao != "":
    resposta = conexao.readline()
    return float(resposta.decode())
  else:
    conexao.close()

while True:
  print(get_sensor())

