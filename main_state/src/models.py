from dataclasses import dataclass


@dataclass
class ConditionValidationValues:
    view_state: str
    view_generator_state: str
    event_validation: str


@dataclass
class CaptchaValidationValues:
    image_url: str = ""
    last_captcha_focus: str = ""
    captcha_placeholder_ct100: str = ""
    captcha_placeholder_validate_button: str = "Continue"
    view_state: str = ""
    view_generator_state: str = ""
    event_target: str = ""
    event_argument: str = ""
    event_validation: str = ""



@dataclass
class PageValidationValues:
    ct100_placeholder_myscript_mgr: str = ""
    event_target: str = ""
    event_argument: str = ""
    view_state: str = ""
    view_generator_state: str = ""
    ct100_placeholder_address_map: str = ""
    view_state_encrypted: str = ""
    event_validation: str = ""
    last_focus: str = ""
