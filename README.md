# Chat_app

Aplikacja czatu typu klient–serwer zrealizowana w języku Python z wykorzystaniem gniazd TCP (`socket`), 
wielowątkowości (`threading`) oraz własnego protokołu komunikacyjnego opartego na formacie JSON i separatorze `\n`.
Projekt zawiera klienta terminalowego (CLI), klienta okienkowego (Tkinter GUI) oraz skrypt porównawczy TCP względem WebSockets.


## Struktura projektu

* `protocol.py` - kodowanie (`encode_message`) i dekodowanie (`decode_messages`) wiadomości w formacie JSON zakończonym znakiem nowej linii (`\n`),
* `server.py` - wielowątkowy serwer TCP obsługujący logowanie, historię wiadomości (do 50 wpisów), rozsyłanie komunikatów (broadcast), komendy, bezpieczne zamykanie,
* `client.py` - logika sieciowa klienta (Client) z ponawianiem połączenia (@retry z pakietu tenacity), kolejką queue.Queue() i wątkiem odbiorczym oraz interfejs konsolowy (run_cli) z obsługą przerwań i zamykania.
* `clientGUI.py` - interfejs graficzny (`ChatApp`) zbudowany w `tkinter`, korzystający z tej samej klasy `Client`.

## Wymagania i zestawienie środowiska

* Python 3.10+
* Moduły ze standardowej biblioteki Pythona: `socket`, `threading`, `queue`, `json`, `time`, `tkinter`, `asyncio`

Instalacja zależności zewnętrznych:
Bash
```bash
pip install tenacity 
```
## Uruchomienie

1. Uruchomienie serwera
```bash
python3 server.py
```
2. Uruchomienie klienta w konsoli (CLI)
```bash
python3 client.py
```
3. Uruchomienie klienta z interfejsem graficznym (GUI)
```bash
python3 clientGUI.py
```
## Przykładowe dane wejściowe
login - "Ania" 

wiadomość - "hej"

komenda - "/ping"

## Dostępne komendy:   
/list – wyświetla listę aktualnie zalogowanych użytkowników,   
/ping – wysyła zapytanie PING i odbiera odpowiedź PONG z serwera,   
/quit – zamyka połączenie i wychodzi z aplikacji. 
