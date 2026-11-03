module ApplicationHelper
  def status_label(status)
    { "waiting" => "Wartend", "active" => "Aktiv", "closed" => "Abgeschlossen" }.fetch(status, status)
  end
end
