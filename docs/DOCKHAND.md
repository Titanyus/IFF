# Beide PoCs mit Dockhand ausprobieren

Zwei getrennte Git-Stacks aus `https://github.com/Titanyus/IFF`, Branch `main`. Die Dateien sind eigenständige Compose-Stacks; nicht zusätzlich mit der normalen `compose.yaml` kombinieren.

| Dockhand-Feld | Rails/Hotwire | Django/Vue |
|---|---|---|
| Stack-Name | `ff-rails-dockhand` | `ff-django-dockhand` |
| Compose file path | `rails-hotwire/compose.dockhand.yaml` | `django-vue/compose.dockhand.yaml` |
| Context directory | Standard / leer lassen | Standard / leer lassen |
| Build images on deploy | **Einschalten** | **Einschalten** |
| Aufruf | `http://SERVER-IP:2501` | `http://SERVER-IP:2502` |

Dockhand verwendet standardmäßig den Ordner der Compose-Datei als Arbeitsverzeichnis. Dadurch stehen die Dockerfiles und ihre jeweiligen Build-Kontexte bereit. Das reine Einfügen der YAML in einen leeren Stack-Editor reicht nicht: Der Quellcode muss mit dem Git-Stack ausgecheckt werden. Bei einem privaten GitHub-Repository dessen Zugriff in Dockhand unter **Settings → Git** konfigurieren. Benötigt wird Dockhands Git-Deployment mit „Build images on deploy“ (laut Handbuch seit 1.0.23) sowie Docker Compose V2 / BuildKit.

## Variablen in Dockhand

Für jeden Stack die passende `.env.dockhand.example` als Vorlage für die Stack-Umgebungsvariablen verwenden. Die Beispiele enthalten absichtlich keine einsatzbereiten Datenbankpasswörter oder Sitzungsschlüssel. Die Werte werden in Dockhand gepflegt, nicht auf GitHub.

Für Rails:

```dotenv
APP_HOST=192.168.1.50
BIND_IP=0.0.0.0
POSTGRES_DB=ff_rails
POSTGRES_USER=ff_demo
POSTGRES_PASSWORD=HIER_EIGENES_DATENBANKPASSWORT_EINTRAGEN
RAILS_SECRET_KEY_BASE=HIER_EIGENEN_LANGEN_ZUFALLSSCHLUESSEL_EINTRAGEN
```

Für Django/Vue:

```dotenv
APP_HOST=192.168.1.50
BIND_IP=0.0.0.0
POSTGRES_DB=ff_django
POSTGRES_USER=ff_demo
POSTGRES_PASSWORD=HIER_EIN_ANDERES_DATENBANKPASSWORT_EINTRAGEN
DJANGO_SECRET_KEY=HIER_EINEN_ANDEREN_LANGEN_ZUFALLSSCHLUESSEL_EINTRAGEN
```

`APP_HOST` auf die tatsächlich im Browser verwendete Server-IP oder den Hostnamen setzen, **ohne** `http://`, Port oder Pfad. Mehrere erlaubte Hosts sind kommasepariert möglich, z. B. `192.168.1.50,ff-demo.intern`. Keine Wildcards verwenden. Nicht freigegebene Hosts werden weiterhin abgewiesen. Bei Zugriff über die IP ist kein zusätzlicher CSRF-Trusted-Origin nötig: Browser und Backend benutzen dieselbe HTTP-Origin.

Passwörter beispielsweise mit `openssl rand -hex 24`, Sitzungsschlüssel mit `openssl rand -hex 64` erzeugen; für jeden Wert einen eigenen Aufruf verwenden. Nach Initialisierung des PostgreSQL-Volumes ändert eine neue `POSTGRES_PASSWORD`-Variable nicht das gespeicherte Datenbankpasswort. Bestehende Volumes bewahren und Passwortänderungen gezielt durchführen.

`BIND_IP=0.0.0.0` veröffentlicht die Ports auf allen IPv4-Hostschnittstellen. Alternativ die konkrete LAN-IP des Docker-Hosts eintragen. Mit `127.0.0.1` ist Zugriff nur direkt auf diesem Host möglich. PostgreSQL hat keinen veröffentlichten Port.

## Betrieb der Demos

Nach dem Deploy zunächst die Logs von `db`, `web` und `nginx` kontrollieren. Der Webdienst wartet auf die gesunde Datenbank, führt Migrationen aus und ergänzt die fiktiven Demodaten. Ein erneuter Start überschreibt bestehende Förderfälle nicht. Jeder Stack hat ein eigenes PostgreSQL-Volume und eigene Netzwerke. Die Dockhand-Demos verwenden andere Projektnamen als die bisherigen lokalen PoCs; vorhandene Daten werden nicht automatisch übernommen. Für getrennte Volumes die beiden Stacks immer unter verschiedenen Namen verwalten.

Demo-Anmeldung in beiden Anwendungen:

- `leitung@example.test`
- `verwaltung@example.test`
- `therapie1@example.test`
- `therapie2@example.test`

Passwort jeweils `DemoPass-2026!`.

Diese Stacks sind für den Vergleich mit fiktiven Daten im vertrauenswürdigen LAN vorgesehen. Sie benutzen HTTP und die bestehenden Demo-Accounts; Rails läuft weiterhin im Entwicklungsmodus. Keine Router-Portweiterleitung ins Internet einrichten und keine echten Kinder-/Gesundheitsdaten verwenden. HTTPS, Domain-/Proxy-Konfiguration und Produktivhärtung sind nicht Teil dieser Änderung.

Nginx-Konfiguration und Vue-Dateien werden in Images eingebaut; es sind keine Host-Bind-Mounts für Konfigurationsdateien nötig. Node wird nur beim Vue-Build benötigt. Die Cloud-spezifische `compose.cloud.yaml` gehört nicht zum normalen Dockhand-Deploy; bei einem eigenen HTTPS-Proxy muss dessen CA gezielt beim Build eingebunden werden.

## Prüfung vor Ablage auf GitHub

Beide Compose-Dateien wurden auf gültige Konfiguration geprüft, erfolgreich gebaut und lokal auf 2501/2502 gestartet. Der HTTP-Test mit explizit erlaubtem Host bestätigte Anmeldung, drei Demofälle, statische Dateien, CSRF-Schutz und Ablehnung fremder Hosts. Rails: 6 Tests / 31 Assertions erfolgreich. Django: 5 Tests erfolgreich. Die Prüfungen liefen in den neuen Stack-Containern; die Portfreigabe wurde dafür auf Loopback begrenzt. Ein tatsächliches Deployment auf dem Dockhand-Server des Benutzers ist hier nicht möglich.

Referenz für die Felder und Build-Optionen: [Dockhand-Handbuch](https://dockhand.pro/manual), Abschnitt „Git integration“.
