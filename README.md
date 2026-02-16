# AnonSurf GUI Control Panel v2.1

**Interfaccia grafica per AnonSurf - Con integrazione Menu di Sistema**

## Novità v2.1

- 🖥️ **Integrazione Menu di Sistema** - Una voce con dialog di scelta
- 🔐 **Dialog grafico con zenity** - Password e selezione versione insieme
- 📌 **Due versioni**: GUI Completa o GUI Minimale (selezione all'avvio)
- 🔗 **Link simbolici** - Avviabile da terminale con `anonsurf-gui` e `anonsurf-gui-mini`
- 📁 **Installazione in /opt** - File organizzati in /opt/anonsurf-gui
- 🎨 **Icona personalizzata** - Visibile nel menu e nel dock
- 🏳️ **68 bandiere PNG embedded** - Nessun download necessario
- ✅ **Funziona offline** - Anche sotto Tor con connessione lenta

## Caratteristiche

- ✅ **Due interfacce**: GUI completa + GUI minimale
- ✅ Ambiente Python isolato con **venv**
- ✅ Avvio/arresto AnonSurf con **verifica robusta** (15 tentativi, 45s max)
- ✅ Visualizzazione **IP reale** e **IP Tor**
- ✅ Informazioni **Exit Node**: IP, hostname, paese, città, regione, ISP
- ✅ **68 bandiere nazionali** embedded (PNG 32x24)
- ✅ Cambio **identità Tor** manuale e automatico
- ✅ **Log dettagliato** con diagnostica errori
- ✅ **Ripristino automatico** della rete alla chiusura

## Requisiti

- **Sistema**: Kali Linux, Parrot OS, LMDE, Debian, Ubuntu
- **Python**: 3.10+ (incluso 3.13)
- **Tk**: 8.6+ (supporto PNG nativo)

## Installazione

```bash
# Estrai il pacchetto
tar -xzf anonsurf-gui-v2.1.tar.gz
cd anonsurf-gui-v2.1

# Installa (richiede root)
sudo ./install.sh
```

L'installer:
1. Installa le dipendenze di sistema
2. Copia i file in `/opt/anonsurf-gui`
3. Crea l'ambiente virtuale Python
4. Installa AnonSurf se mancante
5. Crea i link simbolici in `/usr/local/bin`
6. Aggiunge una voce nel menu di sistema con dialog di scelta

## Avvio

### Dal Menu di Sistema

Cerca nel menu applicazioni: **AnonSurf GUI**

Apparirà una finestra che chiede:
1. La **password** di amministratore
2. La **versione** da avviare (GUI Completa o GUI Minimale)

### Da Terminale

```bash
# GUI completa
sudo anonsurf-gui

# GUI minimale (compatta)
sudo anonsurf-gui-mini

# Dalla directory sorgente
./start.sh        # completa
./start.sh -min   # mini
```

## Struttura Installazione

```
/opt/anonsurf-gui/
├── anonsurf_gui.py           # GUI completa
├── anonsurf_gui_mini.py      # GUI minimale
├── anonsurf-gui-launcher.sh  # Launcher con dialog zenity
├── anonsurf-gui-run.sh       # Script di esecuzione
├── config.ini                # Configurazione
├── venv/                     # Ambiente Python virtuale
└── anonsurf_gui.log          # Log operazioni

/usr/share/applications/
└── anonsurf-gui.desktop      # Voce menu (unica)

/usr/local/bin/
├── anonsurf-gui              # Comando terminale (completa)
└── anonsurf-gui-mini         # Comando terminale (mini)

/usr/share/icons/hicolor/128x128/apps/
└── anonsurf-gui.png          # Icona applicazione
```

## Bandiere Supportate

Le bandiere sono PNG 32x24 pixel embedded come base64 nel codice.
68 paesi supportati:

🇦🇪 AE 🇦🇷 AR 🇦🇹 AT 🇦🇺 AU 🇧🇪 BE 🇧🇬 BG 🇧🇷 BR 🇧🇾 BY 🇨🇦 CA 🇨🇭 CH
🇨🇱 CL 🇨🇳 CN 🇨🇴 CO 🇨🇿 CZ 🇩🇪 DE 🇩🇰 DK 🇪🇪 EE 🇪🇬 EG 🇪🇸 ES 🇫🇮 FI
🇫🇷 FR 🇬🇧 GB 🇬🇷 GR 🇭🇰 HK 🇭🇷 HR 🇭🇺 HU 🇮🇩 ID 🇮🇪 IE 🇮🇱 IL 🇮🇳 IN
🇮🇷 IR 🇮🇸 IS 🇮🇹 IT 🇯🇵 JP 🇰🇪 KE 🇰🇷 KR 🇱🇹 LT 🇱🇺 LU 🇱🇻 LV 🇲🇦 MA
🇲🇩 MD 🇲🇽 MX 🇲🇾 MY 🇳🇬 NG 🇳🇱 NL 🇳🇴 NO 🇳🇿 NZ 🇵🇪 PE 🇵🇭 PH 🇵🇰 PK
🇵🇱 PL 🇵🇹 PT 🇷🇴 RO 🇷🇸 RS 🇷🇺 RU 🇸🇦 SA 🇸🇪 SE 🇸🇬 SG 🇸🇮 SI 🇸🇰 SK
🇹🇭 TH 🇹🇷 TR 🇹🇼 TW 🇺🇦 UA 🇺🇸 US 🇻🇪 VE 🇻🇳 VN 🇿🇦 ZA

## Configurazione

Modifica `/opt/anonsurf-gui/config.ini` per personalizzare:

```ini
[timing]
tor_verify_attempts = 15      # Tentativi verifica bootstrap
tor_verify_interval = 3       # Secondi tra tentativi
refresh_interval = 15000      # Refresh stato (ms)
auto_change_interval = 100000 # Auto-change identità (ms)

[gui]
window_width = 700
window_height = 750
max_log_lines = 100
```

## Disinstallazione

```bash
# Rimuovi solo GUI (mantiene AnonSurf e Tor)
sudo ./uninstall.sh

# Rimozione completa (include AnonSurf e Tor)
sudo ./uninstall.sh --full
```

La disinstallazione rimuove:
- Directory `/opt/anonsurf-gui`
- Voci dal menu di sistema
- Link simbolici
- Icona applicazione

## Risoluzione Problemi

### L'applicazione non appare nel menu

```bash
# Aggiorna il database delle applicazioni
sudo update-desktop-database /usr/share/applications
# Riavvia il file manager o fai logout/login
```

### Tor non si avvia

```bash
# Verifica che Tor non sia già in esecuzione
sudo systemctl stop tor
sudo anonsurf start
```

### Bandiere non visualizzate

Verifica che Tk >= 8.6 sia installato:

```bash
python3 -c "import tkinter; print(tkinter.TkVersion)"
```

Deve restituire 8.6 o superiore.

### Timeout bootstrap

- Verifica connessione internet
- L'ISP potrebbe bloccare Tor
- Considera l'uso di bridge Tor

### Errore "Permission denied"

L'applicazione richiede privilegi root. Usa:
```bash
sudo anonsurf-gui
```

oppure avvia dal menu (richiederà la password).

## Licenza

MIT License - Creato da Red-Penguin

## Changelog

### v2.1
- Integrazione nel menu di sistema con due voci
- Installazione in /opt/anonsurf-gui
- Link simbolici in /usr/local/bin
- Icona personalizzata
- Launcher con richiesta automatica privilegi (pkexec)

### v6.2 (base)
- 68 bandiere PNG embedded come base64
- Zero dipendenze esterne per le bandiere
- Funziona offline e sotto Tor
