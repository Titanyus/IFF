# Architecture Decision Records – Startstand

## ADR-001 – Fachdomäne begrenzt

Entscheidung: Patienten-/Kinderaktenverwaltung für Frühförderung; keine generische ERP-/Plugin-Plattform. Grund: Klare Datenmodelle und weniger technische Altlasten.

## ADR-002 – Modularer Monolith

Entscheidung: Getrennte Fachbereiche innerhalb einer Anwendung mit expliziten Services. Grund: Kleine Einrichtung (~20 Personen), hohe Wartbarkeit, keine Microservice-Komplexität.

## ADR-003 – Relationale Wahrheit

Entscheidung: PostgreSQL, eindeutige fachliche Objekte und Verknüpfungen. Warteliste = Statusansicht, keine Kopie. Grund: Datenkonsistenz und Wiederverwendbarkeit.

## ADR-004 – Zentrale Autorisierung

Entscheidung: Gruppen + Aktenzuordnung; Backend erzwingt Sichtbarkeit/Aktionen. Grund: Therapie benötigt eingeschränkte Sicht, Verwaltung umfassendere Sicht.

## ADR-005 – Löschung zweistufig (zunächst nur Soft Delete)

Entscheidung: Fachlicher Abschluss getrennt von Papierkorb. Keine Hard-Delete-Implementierung im PoC. Gründe: Versehen rückgängig machen, Löschfristen später rechtskonform klären.

## ADR-006 – Stackentscheidung noch offen

Entscheidung: Rails/Hotwire und Django/Vue parallel als kleine, isolierte Vergleichsprojekte; **nicht** beide als Langzeitprodukte pflegen. Nach PoC einen Stack wählen.

## ADR-007 – Lokaler Betrieb als Ziel

Entscheidung: Docker Compose, später Ansible, Nginx/HTTPS, VPN und Borg mit Restore-Playbook. Im PoC nur lokales HTTP auf Loopback.
