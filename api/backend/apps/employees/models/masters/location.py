
from django.db import models

from apps.employees.models.base import MasterBaseModel, MetadataMixin


# ---------------------------------------------------------------------------
# mst_country
# ---------------------------------------------------------------------------


class Country(MetadataMixin):

    

    id = models.SmallAutoField(primary_key=True)
    code = models.CharField(
        max_length=2,
        unique=True,
        help_text="ISO Alpha-2 code, e.g. IN / US",
    )
    iso3_code = models.CharField(
        max_length=3,
        unique=True,
        help_text="ISO Alpha-3 code, e.g. IND / USA",
    )
    numeric_code = models.SmallIntegerField(unique=True, null=True, blank=True)
    label = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "mst_country"
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_country_code"),
            models.Index(fields=["iso3_code"], name="idx_mst_country_iso3"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_country_code"),
            models.UniqueConstraint(fields=["iso3_code"], name="uq_mst_country_iso3"),
            models.CheckConstraint(
                check=models.Q(numeric_code__isnull=True)
                | models.Q(numeric_code__gt=0),
                name="chk_mst_country_numeric_positive",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.label} ({self.code})"


# ---------------------------------------------------------------------------
# mst_state
# ---------------------------------------------------------------------------


class State(MetadataMixin):
   

    id = models.SmallAutoField(primary_key=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        db_column="country_id",
        related_name="states",
    )
    code = models.CharField(max_length=10)
    label = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "mst_state"
        verbose_name = "State"
        verbose_name_plural = "States"
        indexes = [
            models.Index(fields=["country", "code"], name="idx_mst_state_country_code"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(code__gt=""),
                name="chk_mst_state_code_nonempty",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.label} ({self.code})"


# ---------------------------------------------------------------------------
# mst_city
# ---------------------------------------------------------------------------


class City(MetadataMixin):


    id = models.SmallAutoField(primary_key=True)
    state = models.ForeignKey(
        State,
        on_delete=models.PROTECT,
        db_column="state_id",
        related_name="cities",
    )
    code = models.CharField(max_length=10)
    label = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "mst_city"
        verbose_name = "City"
        verbose_name_plural = "Cities"
        indexes = [
            models.Index(fields=["state", "code"], name="idx_mst_city_state_code"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(code__gt=""),
                name="chk_mst_city_code_nonempty",
            ),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_headquarter_location
# ---------------------------------------------------------------------------


class HeadquarterLocation(MetadataMixin):
  

    id = models.SmallAutoField(primary_key=True)
    code = models.CharField(max_length=30, unique=True)
    label = models.CharField(max_length=150)
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        db_column="country_id",
        related_name="hq_locations",
    )
    state = models.ForeignKey(
        State,
        on_delete=models.PROTECT,
        db_column="state_id",
        related_name="hq_locations",
    )
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        db_column="city_id",
        related_name="hq_locations",
    )
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "mst_headquarter_location"
        verbose_name = "Headquarter Location"
        verbose_name_plural = "Headquarter Locations"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_hq_location_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_hq_location_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_office_location
# ---------------------------------------------------------------------------


class OfficeLocation(MetadataMixin):
    

    id = models.SmallAutoField(primary_key=True)
    code = models.CharField(max_length=30, unique=True)
    label = models.CharField(max_length=150)
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        db_column="country_id",
        related_name="office_locations",
    )
    state = models.ForeignKey(
        State,
        on_delete=models.PROTECT,
        db_column="state_id",
        related_name="office_locations",
    )
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        db_column="city_id",
        related_name="office_locations",
    )
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    timezone = models.CharField(
        max_length=60, default="Asia/Kolkata", blank=True, null=True
    )
    is_headquarter = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "mst_office_location"
        verbose_name = "Office Location"
        verbose_name_plural = "Office Locations"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_office_location_code"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["code"], name="uq_mst_office_location_code"
            ),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_production_cell
# ---------------------------------------------------------------------------


class ProductionCell(MetadataMixin):
  

    id = models.SmallAutoField(primary_key=True)
    code = models.CharField(max_length=30, unique=True)
    label = models.CharField(max_length=150)
    office_location = models.ForeignKey(
        OfficeLocation,
        on_delete=models.PROTECT,
        db_column="office_location_id",
        related_name="production_cells",
    )
    department = models.ForeignKey(
        "employees.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="department_id",
        related_name="production_cells",
    )
    capacity = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "mst_production_cell"
        verbose_name = "Production Cell"
        verbose_name_plural = "Production Cells"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_production_cell_code"),
            models.Index(
                fields=["office_location"], name="idx_mst_production_cell_office"
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["code"], name="uq_mst_production_cell_code"
            ),
            models.CheckConstraint(
                check=models.Q(capacity__isnull=True) | models.Q(capacity__gt=0),
                name="chk_mst_production_cell_capacity_positive",
            ),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_floor
# ---------------------------------------------------------------------------


class Floor(MetadataMixin):
   

    id = models.SmallAutoField(primary_key=True)
    office_location = models.ForeignKey(
        OfficeLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="office_location_id",
        related_name="floors",
    )
    floor_number = models.SmallIntegerField()
    label = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "mst_floor"
        verbose_name = "Floor"
        verbose_name_plural = "Floors"
        indexes = [
            models.Index(
                fields=["office_location", "floor_number"],
                name="idx_mst_floor_location_number",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.label} (Floor {self.floor_number})"


# ---------------------------------------------------------------------------
# mst_location_type
# ---------------------------------------------------------------------------


class LocationType(MasterBaseModel):


    code = models.CharField(max_length=30, unique=True)
    label = models.CharField(max_length=100)

    class Meta:
        db_table = "mst_location_type"
        verbose_name = "Location Type"
        verbose_name_plural = "Location Types"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_location_type_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_location_type_code"),
        ]

    def __str__(self) -> str:
        return self.label
