"""Language Details UI — field sets (employee module screenshot)."""

LANGUAGE_PROFICIENCY_ROW_FIELDS = (
    "id",
    "language_id",
    "language",
    "proficiency_level_id",
    "proficiency_level",
    "read_proficiency_id",
    "read_proficiency",
    "write_proficiency_id",
    "write_proficiency",
    "speak_proficiency_id",
    "speak_proficiency",
    "can_read",
    "can_write",
    "can_speak",
    "is_mother_tongue",
)

LANGUAGE_PROFICIENCY_EDITABLE = frozenset({
    "id",
    "language_id",
    "language",
    "proficiency_level_id",
    "proficiency_level",
    "read_proficiency_id",
    "read_proficiency",
    "write_proficiency_id",
    "write_proficiency",
    "speak_proficiency_id",
    "speak_proficiency",
    "can_read",
    "can_write",
    "can_speak",
    "is_mother_tongue",
    "remove",
    "delete",
})
