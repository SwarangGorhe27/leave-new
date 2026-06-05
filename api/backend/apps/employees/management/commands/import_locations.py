import time
import requests

from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import get_tenant_model, tenant_context

from apps.employees.models import (
    City,
    Country,
    State,
)

USERNAME = "pankajpatil"
GEONAMES_BASE_URL = "http://api.geonames.org"


class Command(BaseCommand):

    help = "Import countries, states, and cities from GeoNames."

    def add_arguments(self, parser):

        parser.add_argument(
            "--username",
            default=USERNAME,
            help="GeoNames username",
        )

        parser.add_argument(
            "--timeout",
            type=int,
            default=30,
            help="HTTP timeout",
        )

        parser.add_argument(
            "--schema",
            help="Tenant schema name",
        )

    def _fetch_geonames(self, endpoint, params, timeout):

        # Prevent GeoNames rate limit
        time.sleep(1)

        try:

            response = requests.get(
                f"{GEONAMES_BASE_URL}/{endpoint}",
                params=params,
                timeout=timeout,
            )

            response.raise_for_status()

            payload = response.json()

        except requests.RequestException as exc:
            raise CommandError(
                f"GeoNames request failed: {exc}"
            ) from exc

        except ValueError as exc:
            raise CommandError(
                "GeoNames returned invalid JSON"
            ) from exc

        status = payload.get("status")

        if status:

            message = status.get(
                "message",
                "Unknown GeoNames API error"
            )

            value = status.get("value")

            detail = f" ({value})" if value else ""

            raise CommandError(
                f"GeoNames API error{detail}: {message}"
            )

        geonames = payload.get("geonames")

        if geonames is None:

            raise CommandError(
                "GeoNames response missing 'geonames'"
            )

        return geonames

    def _numeric_code(self, value):

        if value in (None, "", 0, "0"):
            return None

        try:

            value = int(value)

            # Avoid DB constraint issue
            if value <= 0:
                return None

            return value

        except (TypeError, ValueError):
            return None

    def _get_tenant(self, schema):

        TenantModel = get_tenant_model()

        if schema:

            tenant = TenantModel.objects.filter(
                schema_name=schema
            ).first()

            if tenant is None:

                raise CommandError(
                    f"Tenant schema '{schema}' not found"
                )

            return tenant

        tenants = list(
            TenantModel.objects.filter(
                is_active=True
            ).exclude(
                schema_name="public"
            )
        )

        if len(tenants) == 1:
            return tenants[0]

        schemas = ", ".join(
            tenant.schema_name for tenant in tenants
        ) or "none"

        raise CommandError(
            "Pass --schema because multiple tenants exist. "
            f"Available schemas: {schemas}"
        )

    def _import_locations(self, username, timeout):

        self.stdout.write("Importing countries...")

        countries = self._fetch_geonames(
            "countryInfoJSON",
            {"username": username},
            timeout,
        )

        for country in countries:

            country_code = country.get("countryCode")
            iso3_code = country.get("isoAlpha3")
            country_name = country.get("countryName")
            country_geoname_id = country.get("geonameId")

            if not all([
                country_code,
                iso3_code,
                country_name,
                country_geoname_id,
            ]):

                self.stderr.write(
                    f"Skipping incomplete country row: {country}"
                )

                continue

            try:

                country_obj, created = Country.objects.update_or_create(

                    code=country_code,

                    defaults={
                        "label": country_name,
                        "iso3_code": iso3_code,
                        "numeric_code": self._numeric_code(
                            country.get("isoNumeric")
                        ),
                    }
                )

            except Exception as exc:

                self.stderr.write(
                    f"Skipping country {country_name}: {exc}"
                )

                continue

            self.stdout.write(
                f"Country: {country_obj.label}"
            )

            # GET STATES
            try:

                states = self._fetch_geonames(
                    "childrenJSON",
                    {
                        "geonameId": country_geoname_id,
                        "username": username,
                    },
                    timeout,
                )

            except CommandError as exc:

                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping {country_name}: {exc}"
                    )
                )

                continue

            for state in states:

                state_geoname_id = state.get("geonameId")
                state_name = state.get("name")

                if not all([
                    state_geoname_id,
                    state_name,
                ]):

                    self.stderr.write(
                        f"Skipping incomplete state row: {state}"
                    )

                    continue

                try:

                    state_obj, created = State.objects.update_or_create(

                        country=country_obj,
                        code=str(state_geoname_id),

                        defaults={
                            "label": state_name
                        }
                    )

                except Exception as exc:

                    self.stderr.write(
                        f"Skipping state {state_name}: {exc}"
                    )

                    continue

                self.stdout.write(
                    f"   State: {state_obj.label}"
                )

                # GET CITIES
                try:

                    cities = self._fetch_geonames(
                        "childrenJSON",
                        {
                            "geonameId": state_geoname_id,
                            "username": username,
                        },
                        timeout,
                    )

                except CommandError as exc:

                    self.stdout.write(
                        self.style.WARNING(
                            f"Skipping cities for {state_name}: {exc}"
                        )
                    )

                    continue

                for city in cities:

                    city_geoname_id = city.get("geonameId")
                    city_name = city.get("name")

                    if not all([
                        city_geoname_id,
                        city_name,
                    ]):

                        self.stderr.write(
                            f"Skipping incomplete city row: {city}"
                        )

                        continue

                    try:

                        City.objects.update_or_create(

                            state=state_obj,
                            code=str(city_geoname_id),

                            defaults={
                                "label": city_name
                            }
                        )

                        self.stdout.write(
                            f"      City: {city_name}"
                        )

                    except Exception as exc:

                        self.stderr.write(
                            f"Skipping city {city_name}: {exc}"
                        )

                        continue

        self.stdout.write(
            self.style.SUCCESS(
                "ALL DATA IMPORTED SUCCESSFULLY"
            )
        )

    def handle(self, *args, **kwargs):

        username = kwargs["username"]
        timeout = kwargs["timeout"]

        tenant = self._get_tenant(
            kwargs.get("schema")
        )

        self.stdout.write(
            f"Using tenant schema: {tenant.schema_name}"
        )

        with tenant_context(tenant):

            self._import_locations(
                username,
                timeout,
            )