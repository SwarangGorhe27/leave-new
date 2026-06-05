import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django_tenants.utils import get_tenant_model, tenant_context

from apps.employees.models.masters.misc import Language


DEFAULT_CSV_PATH = (
    Path(__file__).resolve().parents[2] / "Language_document" / "language-codes.csv"
)

ISO_639_1_TO_639_2T = {
    "aa": "aar",
    "ab": "abk",
    "ae": "ave",
    "af": "afr",
    "ak": "aka",
    "am": "amh",
    "an": "arg",
    "ar": "ara",
    "as": "asm",
    "av": "ava",
    "ay": "aym",
    "az": "aze",
    "ba": "bak",
    "be": "bel",
    "bg": "bul",
    "bi": "bis",
    "bm": "bam",
    "bn": "ben",
    "bo": "bod",
    "br": "bre",
    "bs": "bos",
    "ca": "cat",
    "ce": "che",
    "ch": "cha",
    "co": "cos",
    "cr": "cre",
    "cs": "ces",
    "cu": "chu",
    "cv": "chv",
    "cy": "cym",
    "da": "dan",
    "de": "deu",
    "dv": "div",
    "dz": "dzo",
    "ee": "ewe",
    "el": "ell",
    "en": "eng",
    "eo": "epo",
    "es": "spa",
    "et": "est",
    "eu": "eus",
    "fa": "fas",
    "ff": "ful",
    "fi": "fin",
    "fj": "fij",
    "fo": "fao",
    "fr": "fra",
    "fy": "fry",
    "ga": "gle",
    "gd": "gla",
    "gl": "glg",
    "gn": "grn",
    "gu": "guj",
    "gv": "glv",
    "ha": "hau",
    "he": "heb",
    "hi": "hin",
    "ho": "hmo",
    "hr": "hrv",
    "ht": "hat",
    "hu": "hun",
    "hy": "hye",
    "hz": "her",
    "ia": "ina",
    "id": "ind",
    "ie": "ile",
    "ig": "ibo",
    "ii": "iii",
    "ik": "ipk",
    "io": "ido",
    "is": "isl",
    "it": "ita",
    "iu": "iku",
    "ja": "jpn",
    "jv": "jav",
    "ka": "kat",
    "kg": "kon",
    "ki": "kik",
    "kj": "kua",
    "kk": "kaz",
    "kl": "kal",
    "km": "khm",
    "kn": "kan",
    "ko": "kor",
    "kr": "kau",
    "ks": "kas",
    "ku": "kur",
    "kv": "kom",
    "kw": "cor",
    "ky": "kir",
    "la": "lat",
    "lb": "ltz",
    "lg": "lug",
    "li": "lim",
    "ln": "lin",
    "lo": "lao",
    "lt": "lit",
    "lu": "lub",
    "lv": "lav",
    "mg": "mlg",
    "mh": "mah",
    "mi": "mri",
    "mk": "mkd",
    "ml": "mal",
    "mn": "mon",
    "mr": "mar",
    "ms": "msa",
    "mt": "mlt",
    "my": "mya",
    "na": "nau",
    "nb": "nob",
    "nd": "nde",
    "ne": "nep",
    "ng": "ndo",
    "nl": "nld",
    "nn": "nno",
    "no": "nor",
    "nr": "nbl",
    "nv": "nav",
    "ny": "nya",
    "oc": "oci",
    "oj": "oji",
    "om": "orm",
    "or": "ori",
    "os": "oss",
    "pa": "pan",
    "pi": "pli",
    "pl": "pol",
    "ps": "pus",
    "pt": "por",
    "qu": "que",
    "rm": "roh",
    "rn": "run",
    "ro": "ron",
    "ru": "rus",
    "rw": "kin",
    "sa": "san",
    "sc": "srd",
    "sd": "snd",
    "se": "sme",
    "sg": "sag",
    "si": "sin",
    "sk": "slk",
    "sl": "slv",
    "sm": "smo",
    "sn": "sna",
    "so": "som",
    "sq": "sqi",
    "sr": "srp",
    "ss": "ssw",
    "st": "sot",
    "su": "sun",
    "sv": "swe",
    "sw": "swa",
    "ta": "tam",
    "te": "tel",
    "tg": "tgk",
    "th": "tha",
    "ti": "tir",
    "tk": "tuk",
    "tl": "tgl",
    "tn": "tsn",
    "to": "ton",
    "tr": "tur",
    "ts": "tso",
    "tt": "tat",
    "tw": "twi",
    "ty": "tah",
    "ug": "uig",
    "uk": "ukr",
    "ur": "urd",
    "uz": "uzb",
    "ve": "ven",
    "vi": "vie",
    "vo": "vol",
    "wa": "wln",
    "wo": "wol",
    "xh": "xho",
    "yi": "yid",
    "yo": "yor",
    "za": "zha",
    "zh": "zho",
    "zu": "zul",
}


def normalize_required(value):
    return (value or "").strip()


class Command(BaseCommand):
    help = "Import language master data from apps/employees/Language_document/language-codes.csv."

    def add_arguments(self, parser):
        parser.add_argument(
            "--schema",
            type=str,
            required=True,
            help="Tenant schema name to import language data into.",
        )
        parser.add_argument(
            "--csv-path",
            type=str,
            default=str(DEFAULT_CSV_PATH),
            help="CSV file path. Defaults to apps/employees/Language_document/language-codes.csv.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Number of records to insert/update per batch.",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"])
        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        TenantModel = get_tenant_model()
        try:
            tenant = TenantModel.objects.get(schema_name=options["schema"])
        except TenantModel.DoesNotExist as exc:
            raise CommandError(
                f"Tenant with schema '{options['schema']}' not found"
            ) from exc

        batch_size = options["batch_size"]
        if batch_size <= 0:
            raise CommandError("--batch-size must be greater than 0")

        with tenant_context(tenant):
            imported, created, updated = self.import_csv(csv_path, batch_size)

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {imported} rows into mst_language "
                f"({created} created, {updated} updated)."
            )
        )

    def import_csv(self, csv_path, batch_size):
        imported = created = updated = 0
        batch = []

        with csv_path.open(newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)
            missing_headers = {"alpha2", "English"} - set(reader.fieldnames or [])
            if missing_headers:
                raise CommandError(
                    "CSV is missing required column(s): "
                    + ", ".join(sorted(missing_headers))
                )

            for row_number, row in enumerate(reader, start=2):
                alpha2 = normalize_required(row.get("alpha2")).lower()
                label = normalize_required(row.get("English"))
                if not alpha2 or not label:
                    raise CommandError(
                        f"CSV row {row_number} must include alpha2 and English."
                    )
                if len(alpha2) != 2:
                    raise CommandError(
                        f"CSV row {row_number} has invalid alpha2 code: {alpha2}"
                    )

                iso_639_2_code = ISO_639_1_TO_639_2T.get(alpha2)
                if not iso_639_2_code:
                    raise CommandError(
                        f"CSV row {row_number} has no ISO 639-2 mapping for alpha2 '{alpha2}'."
                    )

                batch.append(
                    {
                        "code": alpha2,
                        "label": label,
                        "iso_639_2_code": iso_639_2_code,
                        "is_active": True,
                    }
                )

                if len(batch) >= batch_size:
                    batch_created, batch_updated = self.upsert_batch(batch)
                    created += batch_created
                    updated += batch_updated
                    imported += len(batch)
                    batch = []

            if batch:
                batch_created, batch_updated = self.upsert_batch(batch)
                created += batch_created
                updated += batch_updated
                imported += len(batch)

        return imported, created, updated

    @transaction.atomic
    def upsert_batch(self, rows):
        codes = [row["code"] for row in rows]
        iso_codes = [row["iso_639_2_code"] for row in rows]
        existing_by_code = {
            language.code: language
            for language in Language.objects.filter(code__in=codes)
        }
        conflicting_iso_codes = set(
            Language.objects.filter(iso_639_2_code__in=iso_codes)
            .exclude(code__in=codes)
            .values_list("iso_639_2_code", flat=True)
        )
        if conflicting_iso_codes:
            raise CommandError(
                "ISO 639-2 code already exists for another language code: "
                + ", ".join(sorted(conflicting_iso_codes))
            )

        to_create = []
        to_update = []
        update_fields = ["label", "iso_639_2_code", "is_active"]

        for row in rows:
            language = existing_by_code.get(row["code"])
            if language is None:
                to_create.append(Language(**row))
                continue
            for field in update_fields:
                setattr(language, field, row[field])
            to_update.append(language)

        if to_create:
            Language.objects.bulk_create(to_create, batch_size=len(to_create))
        if to_update:
            Language.objects.bulk_update(
                to_update,
                update_fields,
                batch_size=len(to_update),
            )

        return len(to_create), len(to_update)
