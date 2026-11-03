# Sicherheitsmodell, Grenze und Prüfpunkte

**Warnung:** Die mitgelieferten PoCs sind nicht für reale Kinder-, Gesundheits- oder Sozialdaten geeignet. Demo-Login und reines lokales HTTP sind nicht produktionsgeeignet.

## Im PoC demonstriert

- Passwörter werden mittels Framework-Hashing gespeichert (Rails `has_secure_password` / Django `User`).
- Authentifizierte Cookie-Sessions und CSRF-Schutz für schreibende Endpunkte.
- Rollen: `Leitung`, `Verwaltung`, `Therapie`. Therapeutische Liste serverseitig auf zugewiesene Fälle beschränkt.
- Keine PostgreSQL-Portfreigabe am Host, Webserver nur an `127.0.0.1` gebunden.
- Soft Delete getrennt von fachlichem Status, Audit von Statuswechseln.
- Keine extern geladenen Schriftarten/CDNs im Anwendungsfrontend.

## Vor jedem Produktiveinsatz erforderlich

HTTPS auch im LAN, sichere Cookies, vollständige Rechte-Matrix (auch Dokument-, Feld-, Export- und API-Berechtigungen), MFA oder vergleichbarer Zugangsschutz, Sperr-/Passwort-/Session-Konzept, sorgfältige HTTP-Security-Header, Begrenzung von Login-Versuchen, Sicherheitsupdates, Dependency-/Image-Scans, Secrets-Management, Netzwerkhärtung, Logs ohne sensible Inhalte, Auftrags-/Datenschutzprüfung, Lösch- und Aufbewahrungskonzept, verschlüsselte Backups, getrennte Backup-Schlüssel und regelmäßige Restore-Tests. Vorab rechtlich prüfen, ob eine Datenschutz-Folgenabschätzung erforderlich ist.

## Negative Tests

- Therapeut A erhält weder Listen- noch Detaildaten von Fall B.
- Therapeut kann Statuswechsel nicht per direktem HTTP-Request ausführen.
- Nur Leitung erhält Zugriff auf Papierkorb und Wiederherstellung.
- Änderungen erzeugen Auditereignis, unberechtigte Versuche nicht.
- Anonymes Abrufen von Falllisten/Details liefert keine personenbezogenen Daten.

## Backups und Soft Delete

Soft Delete ersetzt keine rechtswirksame Datenlöschung; Regeln und Fristen werden gesondert konzipiert. Ein Backup muss Datenbank und zukünftige Dokumentdateien konsistent abbilden. RTO/RPO sind Ziele, keine Garantien, bis eine reale Testwiederherstellung erfolgreich gemessen wurde.
