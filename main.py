from machine import Pin
import dht
import time
import network
import socket
import gc
d = dht.DHT11(Pin(0))


led = Pin(2, Pin.OUT)

ssid = 'zarizeni_sveta'
password = 'rentales'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

wlan.connect(ssid, password)

# Wait for Wi-Fi connection
connection_timeout = 10
while connection_timeout > 0:
    if wlan.status() >= 3:
        break
    connection_timeout -= 1
    print('Waiting for Wi-Fi connection...')
    time.sleep(1)

# Check if connection is successful
if wlan.status() != 3:
    raise RuntimeError('Failed to establish a network connection')
else:
    print('Connection successful!')
    network_info = wlan.ifconfig()
    print('IP address:', network_info[0])

def start_server():
    gc.collect()  # uvolnění paměti

    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()

    try:
        s.bind(addr)
    except OSError as e:
        print("Port 80 je již obsazen. Restartuj zařízení.")
        raise e

    s.listen(1)
    print('Server běží na', addr)

    while True:
        cl, addr = s.accept()
        print('Klient připojen z', addr)

        try:
            d.measure()
            temp = d.temperature()
            hum = d.humidity()

            request = cl.recv(1024)
            request = str(request)

            response = dthdata(temp, hum)
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(response)
        except Exception as e:
            print('Chyba:', e)
        finally:
            cl.close()


# Adjust dthdata to take temp and hum
def dthdata(temp, hum):
    try:
        with open("index.html", "r") as f:
            html = f.read()
        return html.replace("{{temp}}", str(temp)).replace("{{hum}}", str(hum))
    except Exception as e:
        return f"<html><body><h1>Error loading HTML: {e}</h1></body></html>"


if wlan.status()==3:
    start_server()
