class CareCaseTransitions
  class Invalid < StandardError; end

  def self.call!(care_case:, actor:, target:, effective_on:)
    day = Date.iso8601(effective_on.to_s)
    care_case.with_lock do
      raise Invalid, "Gelöschte Fälle können nicht bearbeitet werden." if care_case.deleted?
      previous = care_case.status
      case [previous, target]
      when %w[waiting active]
        raise Invalid, "Förderbeginn liegt vor der Anmeldung." if day < care_case.requested_on
        care_case.started_on = day
      when %w[active closed]
        raise Invalid, "Abschlussdatum liegt vor dem Förderbeginn." if care_case.started_on.nil? || day < care_case.started_on
        care_case.ended_on = day
      else
        raise Invalid, "Dieser Statuswechsel ist nicht erlaubt."
      end
      care_case.status = target
      care_case.save!
      AuditEvent.create!(care_case: care_case, actor: actor, action: "status", from_status: previous, to_status: target)
    end
    care_case
  rescue ArgumentError
    raise Invalid, "Ein gültiges Datum ist erforderlich."
  end
end
