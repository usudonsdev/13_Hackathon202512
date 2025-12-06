classDiagram
    class User {
        +String userId
        +String name
        +List~BaseLifeTask~ baseTasks
        +List~Friend~ friends
        +syncWithGoogleCalendar()
        +getFreeTimeSlots()
    }

    class Event {
        +String eventId
        +DateTime startDateTime
        +DateTime endDateTime
        +String title
        +String memo
        +EventType type
        +PrivacyStatus privacy
        +isEditable()
    }

    class BaseLifeTask {
        +String name
        +TimeDuration duration
        +String description
        note: "基礎的な生活行為\n(移動、準備など)"
    }

    class TimeSlot {
        +DateTime slotStart
        +Boolean isOccupied
        +Event refEvent
        note: "30分単位で管理するための最小単位"
    }

    class ScheduleManager {
        +recommendSlot(criteria)
        +checkWeather(date)
        +parseNaturalLanguage(text)
    }

    class PrivacyStatus {
        <<enumeration>>
        PUBLIC
        PRIVATE
        FRIEND_ONLY
    }

    User "1" *-- "many" Event : maintains
    User "1" o-- "many" BaseLifeTask : defines
    User "1" o-- "many" User : friends
    Event -- PrivacyStatus : has
    ScheduleManager ..> User : analyzes
    ScheduleManager ..> Event : manages