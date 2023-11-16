from loguru import logger
from tortoise import fields, Model


class OffendersData(Model):
    first_name = fields.CharField(max_length=255, null=True)
    last_name = fields.CharField(max_length=255, null=True)
    middle_name = fields.CharField(max_length=255, null=True)
    suffix = fields.CharField(max_length=255, null=True)
    aliases = fields.JSONField(null=True)
    gender = fields.CharField(max_length=255, null=True)
    race = fields.CharField(max_length=255, null=True)
    birth_date = fields.CharField(max_length=255, null=True)
    addresses = fields.JSONField(null=True)
    height = fields.CharField(max_length=255, null=True)
    weight = fields.CharField(max_length=255, null=True)
    hair_color = fields.CharField(max_length=255, null=True)
    eye_color = fields.CharField(max_length=255, null=True)
    conviction_date = fields.CharField(max_length=255, null=True)
    conviction_state = fields.CharField(max_length=255, null=True)
    predator = fields.CharField(max_length=255, null=True)
    absconder = fields.CharField(max_length=255, null=True)
    registration_date = fields.CharField(max_length=255, null=True)
    residence_verification_date = fields.CharField(max_length=255, null=True)
    leveling = fields.CharField(max_length=255, null=True)
    images = fields.JSONField(null=True)


    @classmethod
    async def add_offender(
            cls,
            first_name: str = None,
            last_name: str = None,
            middle_name: str = None,
            suffix: str = None,
            aliases: list = None,
            gender: str = None,
            race: str = None,
            birth_date: str = None,
            addresses: list = None,
            height: str = None,
            weight: str = None,
            hair_color: str = None,
            eye_color: str = None,
            conviction_date: str = None,
            conviction_state: str = None,
            predator: str = None,
            absconder: str = None,
            registration_date: str = None,
            residence_verification_date: str = None,
            leveling: str = None,
            images: list = None,
    ):
        try:
            await cls.create(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                suffix=suffix,
                aliases={"aliases": aliases},
                gender=gender,
                race=race,
                birth_date=birth_date,
                addresses={"addresses": addresses},
                height=height,
                weight=weight,
                hair_color=hair_color,
                eye_color=eye_color,
                conviction_date=conviction_date,
                conviction_state=conviction_state,
                predator=predator,
                absconder=absconder,
                registration_date=registration_date,
                residence_verification_date=residence_verification_date,
                leveling=leveling,
                images={"images": images},
            )
        except Exception as error:
            logger.error(
                f"Error while adding offender to database: {error}"
            )
