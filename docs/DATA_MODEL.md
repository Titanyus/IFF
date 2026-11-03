# Fachliches Datenmodell – PoC

## Begriffe und Kardinalitäten

```text
User ──< Membership >── Group
  │
  └──< CaseAssignment >── CareCase ──> Child
                                 │
                                 └──< AuditEvent
Child ──< ChildGuardian >── Guardian
```

**Kind** ist eine fachliche Person, kein Förderfall. **Guardian** ist eine Bezugsperson/Sorgeberechtigte; die Beziehung ist eine separate Zuordnung (beispielsweise bei Geschwistern wiederverwendbar). **Förderfall** ist ein Vorgang mit eigener Anmeldung, Status- und Förderhistorie. Eine Person kann mehrere Förderfälle über die Zeit haben.

**User** ist die technische Anmeldung. Spätere Personaldaten eines Mitarbeiters gehören in eine getrennte Personal-Entität, die ggf. auf User verweist (im PoC noch nicht implementiert).

## Statuskonzept

Fachstatus `waiting`, `active`, `closed` (im Display „Wartend“, „Aktiv“, „Abgeschlossen“). Erlaubt sind zunächst nur `waiting → active` (Startdatum erforderlich) und `active → closed` (Enddatum >= Beginn). Andere Fachstatus/Übergänge werden erst nach Gesprächen mit der Frühförderung festgelegt.

`deleted_at` ist **kein Fachstatus**. Ein Papierkorb-Datensatz ist standardmäßig nicht sichtbar; nur Leitung darf ihn sehen, wiederherstellen und löschen markieren. Im PoC gibt es ausdrücklich **keine echte physische Löschung** und keine automatische Aufbewahrungsregel.

## Datenqualität und Ereignisse

Statuswechsel erhalten ein AuditEvent mit Akteur, vorher/nachher, Zeitstempel. Ein Kind wird nicht als Kopie in die Warteliste verschoben. Beim Wechsel auf „aktiv“ bleibt dasselbe CareCase-Objekt bestehen. Nach Abschluss und späterer Rückkehr wird ein **neuer** CareCase zum selben Kind eröffnet (Folgefunktion; der PoC erzeugt bei der UI-Neuanlage zunächst ein neues Kind und dessen ersten Fall).

## Bewusste Auslassungen

Noch keine Bescheide/Kostenträger, fachlichen Texte, Dokumentversionen, Aktenrestriktionen auf Feldebene, Löschfristen, rechtsverbindliche Historie, Freigaben oder Abrechnung. Diese dürfen nicht stillschweigend als triviale zusätzliche Felder ergänzt werden.
