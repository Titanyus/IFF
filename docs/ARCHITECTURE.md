# Architektur – PoC und langfristige Leitplanken

## Vergleich

- **A:** Rails + Turbo/Hotwire + serverseitige HTML-Views + PostgreSQL.
- **B:** Django + sessionbasierte JSON-API + Vue 3 (gebaut mit Vite) + PostgreSQL.
- Beide laufen jeweils in einem eigenen Docker-Compose-Stack (Web, DB, Nginx), Datenbankcontainer nicht am Host publiziert; Nginx nur an `127.0.0.1` (PoC).

## Stabile Grenzen

**Technischer Kern:** Login, Benutzer, Gruppen, zentrale Rechte/Policies, Audit.

**Fachlicher Kern:** Kind, Sorgeberechtigte, Förderfall, Therapiezuordnung. Mehrere Förderfälle pro Kind; keine „Wartelisten-Tabelle“. Warteliste = Statusfilter.

**Künftige interne Module:** Dokumente, Termine, Leistungen, Statistik, Buchhaltungsexport. Keine separaten Prozesse, Datenbanken oder Plugin-API voreilig aufbauen. Datenzugriff über definierte Services und Berechtigungsschicht.

## Zuständigkeitsregel

- Backend ist die **einzige Autorität** für Berechtigungen, Transitionen, Auditereignisse und Validierung.
- Frontend zeigt nur berechtigte, vom Backend freigegebene Daten.
- Relationale Kerndaten sauber modellieren; `JSONB` nur später für nachvollziehbar definierte Zusatzfelder mit Schema und Validierung.
- Fachliche Änderungen als ausdrücklich benannte Aktionen statt beliebiger CRUD-Patches.

## Mehrinstanzbetrieb

Zunächst **eine Einrichtung pro Installation**. Falls später mehrere Einrichtungen: getrennte Installationen, Datenbanken und Schlüssel sind zunächst sicherer/einfacher als ein gemeinsam genutztes Multi-Tenant-System. Keine Einrichtungen-IDs in alle Tabellen „auf Vorrat“ einbauen.

## Entwicklungsbetrieb vs Produktion

Der PoC verwendet HTTP **nur auf Loopback**. Noch kein HTTPS/VPN, Ansible, Borg, revisionsfeste Historie oder realer Dokumentenspeicher. Daten dürfen nicht echt sein.

Später: Ansible, Docker + Compose, Nginx mit HTTPS, nur VPN für externen Zugriff, getrennte Netzwerke, Backups mit konsistenter PostgreSQL-Sicherung + Dokumentdateien, Schlüsselschutz, Wiederherstellungsproben, automatische Sicherheitstests und Updateverfahren. Ziel-RTO bei **reinem Hardwareausfall** ca. 1–2 Stunden, RPO erst nach fachlicher Klärung. Nach Kompromittierung vor Restore Ursachenanalyse und sichere Neuinstallation.
