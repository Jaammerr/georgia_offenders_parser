import base64
import sys
import aiofiles
import httpx
import pyuseragents

from bs4 import BeautifulSoup
from loguru import logger

from src.captcha import Captcha
from src.models import *
from src.models import PageValidationValues
from database import *


class Parser(httpx.AsyncClient):
    def __init__(self, config: dict):
        super().__init__()

        self.config: dict = config
        self.user_agent: str = pyuseragents.random()
        self.headers = {
            'authority': 'state.sor.gbi.ga.gov',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9,ru;q=0.8',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://state.sor.gbi.ga.gov',
            'referer': 'https://state.sor.gbi.ga.gov/Sort_Public/',
            'user-agent': pyuseragents.random(),
        }
        self.timeout = 30
        self.verify = False


    async def get_condition_validation_values(self) -> ConditionValidationValues:
        response = await self.get("https://state.sor.gbi.ga.gov/Sort_Public/")
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        view_state_element = soup.find("input", {"id": "__VIEWSTATE"})
        if view_state_element is None:
            raise ValueError("Can't find __VIEWSTATE element")

        view_state_generator_element = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})
        if view_state_generator_element is None:
            raise ValueError("Can't find __VIEWSTATEGENERATOR element")

        event_validation_element = soup.find("input", {"id": "__EVENTVALIDATION"})
        if event_validation_element is None:
            raise ValueError("Can't find __EVENTVALIDATION element")

        view_state_value = view_state_element["value"]
        view_state_generator_value = view_state_generator_element["value"]
        event_validation_value = event_validation_element["value"]

        return ConditionValidationValues(
            view_state=view_state_value,
            view_generator_state=view_state_generator_value,
            event_validation=event_validation_value
        )

    @staticmethod
    async def get_captcha_validation_values(html: str) -> CaptchaValidationValues:
        soup = BeautifulSoup(html, "html.parser")

        last_focus_element = soup.find("input", {"id": "__LASTFOCUS"})
        if last_focus_element is None:
            raise ValueError("Can't find __LASTFOCUS element")

        captcha_placeholder_ct100_element = soup.find("input", {"id": "LBD_VCT_captcha_ctl00_contentplaceholder1_botdetectcaptcha"})
        if captcha_placeholder_ct100_element is None:
            raise ValueError("Can't find captcha placeholder element")

        view_state_element = soup.find("input", {"id": "__VIEWSTATE"})
        if view_state_element is None:
            raise ValueError("Can't find __VIEWSTATE element")

        view_state_generator_element = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})
        if view_state_generator_element is None:
            raise ValueError("Can't find __VIEWSTATEGENERATOR element")

        event_target_element = soup.find("input", {"id": "__EVENTTARGET"})
        if event_target_element is None:
            raise ValueError("Can't find __EVENTTARGET element")

        event_argument_element = soup.find("input", {"id": "__EVENTARGUMENT"})
        if event_argument_element is None:
            raise ValueError("Can't find __EVENTARGUMENT element")

        event_validation_element = soup.find("input", {"id": "__EVENTVALIDATION"})
        if event_validation_element is None:
            raise ValueError("Can't find __EVENTVALIDATION element")

        captcha_image_element = soup.find("img", {"id": "captcha_ctl00_contentplaceholder1_botdetectcaptcha_CaptchaImage"})
        if captcha_image_element is None:
            raise ValueError("Can't find captcha image element")


        last_focus_value = last_focus_element["value"]
        captcha_placeholder_ct100_value = captcha_placeholder_ct100_element["value"]
        view_state_value = view_state_element["value"]
        view_state_generator_value = view_state_generator_element["value"]
        event_target_value = event_target_element["value"]
        event_argument_value = event_argument_element["value"]
        event_validation_value = event_validation_element["value"]
        captcha_image_url = f'https://state.sor.gbi.ga.gov/Sort_Public/{captcha_image_element["src"]}'

        return CaptchaValidationValues(
            image_url=captcha_image_url,
            last_captcha_focus=last_focus_value,
            captcha_placeholder_ct100=captcha_placeholder_ct100_value,
            view_state=view_state_value,
            view_generator_state=view_state_generator_value,
            event_target=event_target_value,
            event_argument=event_argument_value,
            event_validation=event_validation_value
        )

    @staticmethod
    async def get_page_validation_values(html: str) -> PageValidationValues:
        soup = BeautifulSoup(html, "html.parser")

        # placeholder_myscript_mgr_element = soup.find("input", {"id": "ctl00_ContentPlaceHolder1_myScriptMgr_HiddenField"})
        # if placeholder_myscript_mgr_element is None:
        #     raise ValueError("Can't find placeholder myScriptMgr element")
        #
        #
        # placeholder_address_map_element = soup.find("input", {"id": "ctl00_ContentPlaceHolder1_AddressMap_ClientState"})
        # if placeholder_address_map_element is None:
        #     raise ValueError("Can't find placeholder AddressMap element")


        last_focus_element = soup.find("input", {"id": "__LASTFOCUS"})
        if last_focus_element is None:
            last_focus_value = ""
        else:
            last_focus_value = last_focus_element["value"]

        view_state_element = soup.find("input", {"id": "__VIEWSTATE"})
        if view_state_element is None:
            view_state_value = ""
        else:
            view_state_value = view_state_element["value"]

        view_state_generator_element = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})
        if view_state_generator_element is None:
            view_state_generator_value = ""
        else:
            view_state_generator_value = view_state_generator_element["value"]

        view_state_encrypted_element = soup.find("input", {"id": "__VIEWSTATEENCRYPTED"})
        if view_state_encrypted_element is None:
            view_state_encrypted_value = ""
        else:
            view_state_encrypted_value = view_state_encrypted_element["value"]

        event_target_element = soup.find("input", {"id": "__EVENTTARGET"})
        if event_target_element is None:
            event_target_value = ""
        else:
            event_target_value = event_target_element["value"]

        event_argument_element = soup.find("input", {"id": "__EVENTARGUMENT"})
        if event_argument_element is None:
            event_argument_value = ""
        else:
            event_argument_value = event_argument_element["value"]

        event_validation_element = soup.find("input", {"id": "__EVENTVALIDATION"})
        if event_validation_element is None:
            event_validation_value = ""
        else:
            event_validation_value = event_validation_element["value"]


        placeholder_address_map_element = soup.find("input", {"id": "ctl00_ContentPlaceHolder1_AddressMap_ClientState"})
        if placeholder_address_map_element is None:
            placeholder_address_map_value = ""
        else:
            placeholder_address_map_value = placeholder_address_map_element["value"]

        placeholder_myscript_mgr_value = ""
        scripts = soup.find_all("script")
        for script in scripts:
            try:
                if str(script["src"]).startswith("/Sort_Public/OffenderSearchResults.aspx?_TSM_HiddenField_=ctl00_ContentPlaceHolder1_myScriptMgr_HiddenField"):
                    placeholder_myscript_mgr_value = script["src"].strip("/Sort_Public/OffenderSearchResults.aspx?_TSM_HiddenField_=ctl00_ContentPlaceHolder1_myScriptMgr_HiddenField&_TSM_CombinedScripts_=")
                    break

            except KeyError:
                continue


        return PageValidationValues(
            view_state=view_state_value,
            view_generator_state=view_state_generator_value,
            ct100_placeholder_myscript_mgr=placeholder_myscript_mgr_value,
            ct100_placeholder_address_map=placeholder_address_map_value,
            event_target=event_target_value,
            event_argument=event_argument_value,
            event_validation=event_validation_value,
            view_state_encrypted=view_state_encrypted_value,
            last_focus=last_focus_value,
        )


    async def accept_conditions_of_use(self, validation_values: ConditionValidationValues | PageValidationValues) -> str:
        """Accept conditions of use, after than will be redirected to captcha page"""
        url = "https://state.sor.gbi.ga.gov/Sort_Public/ConditionsOfUse.Aspx"

        data = {
            "__VIEWSTATE": validation_values.view_state,
            "__VIEWSTATEGENERATOR": validation_values.view_generator_state,
            "__EVENTVALIDATION": validation_values.event_validation,
            'ctl00$ContentPlaceHolder1$btnAgree': 'I agree'
        }

        response = await self.post(url, data=data, follow_redirects=True)
        response.raise_for_status()

        return response.text


    async def solve_captcha(self, image_url: str) -> str:
        """Solve captcha using 2Captcha service"""

        response = await self.get(image_url)
        response.raise_for_status()

        async with aiofiles.open("../captcha.jpeg", "wb") as f:
            await f.write(response.content)

        async with aiofiles.open("../captcha.jpeg", 'rb') as f:
            result = await Captcha(
                image_data=str(base64.b64encode(await f.read()), "utf-8"),
                api_key=self.config["two_captcha_api_key"],
            ).solve()

        return result


    async def send_captcha_solution(self, captcha_solution: str, captcha_validation_values: CaptchaValidationValues) -> PageValidationValues:
        """Send captcha solution to server"""
        url = "https://state.sor.gbi.ga.gov/Sort_Public/Captcha.aspx"

        data = {
            '__LASTFOCUS': captcha_validation_values.last_captcha_focus,
            'LBD_VCT_captcha_ctl00_contentplaceholder1_botdetectcaptcha': captcha_validation_values.captcha_placeholder_ct100,
            '__VIEWSTATE': captcha_validation_values.view_state,
            'ctl00$ContentPlaceHolder1$CodeTextBox': captcha_solution.upper(),
            'ctl00$ContentPlaceHolder1$ValidateButton': 'Continue',
            '__VIEWSTATEGENERATOR': captcha_validation_values.view_generator_state,
            '__EVENTTARGET': captcha_validation_values.event_target,
            '__EVENTARGUMENT': captcha_validation_values.event_argument,
            '__EVENTVALIDATION': captcha_validation_values.event_validation,
        }

        response = await self.post(url, data=data, follow_redirects=True)
        response.raise_for_status()

        if response.url == "https://state.sor.gbi.ga.gov/Sort_Public/SearchOffender.aspx":
            page_validation_values = await self.get_page_validation_values(response.text)
            return page_validation_values

        else:
            logger.error("Captcha solution is wrong, trying again..")
            captcha_validation_values = await self.get_captcha_validation_values(response.text)
            captcha_text = await self.solve_captcha(captcha_validation_values.image_url)
            await self.send_captcha_solution(captcha_text, captcha_validation_values)


    async def search_offenders(self, validation_values: PageValidationValues) -> tuple[PageValidationValues, str]:
        url = "https://state.sor.gbi.ga.gov/Sort_Public/SearchOffender.aspx"

        data = {
            'ctl00$ContentPlaceHolder1$MyScriptManager1': "ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$btnSearch",
            "__LASTFOCUS": validation_values.last_focus,
            "__EVENTTARGET": validation_values.event_target,
            "__EVENTARGUMENT": validation_values.event_argument,
            "__VIEWSTATE": validation_values.view_state,
            "__VIEWSTATEGENERATOR": validation_values.view_generator_state,
            "__VIEWSTATEENCRYPTED": validation_values.view_state_encrypted,
            "__EVENTVALIDATION": validation_values.event_validation,
            "ctl00$ContentPlaceHolder1$ddOffenderType": "All sexual offenders. Incarcerated offenders are excluded when location criteria (i.e. county, address, etc.) is provided.",
            "ctl00$ContentPlaceHolder1$ddOffense": "All",
            "ctl00$ContentPlaceHolder1$txtFirstName": "",
            "ctl00$ContentPlaceHolder1$txtLastName": "",
            "ctl00$ContentPlaceHolder1$ddCounty": "All",
            "ctl00$ContentPlaceHolder1$rbGender": "All",
            "ctl00$ContentPlaceHolder1$ddRace": 0,
            "ctl00$ContentPlaceHolder1$rbIncarcerated": "No",
            "ctl00$ContentPlaceHolder1$txtStreet": "",
            "ctl00$ContentPlaceHolder1$ddCity": "All",
            "ctl00$ContentPlaceHolder1$txtZipCode": "",
            "ctl00$ContentPlaceHolder1$txtDistance": "",
            "__ASYNCPOST": True,
            "ctl00$ContentPlaceHolder1$btnSearch": "Search"
        }


        response = await self.post(url, data=data, follow_redirects=True)
        response.raise_for_status()

        response = await self.get("https://state.sor.gbi.ga.gov/Sort_Public/OffenderSearchResults.aspx")
        response.raise_for_status()

        return await self.get_page_validation_values(response.text), response.text


    async def open_page(self, validation_values: PageValidationValues, index: str) -> PageValidationValues:
        url = "https://state.sor.gbi.ga.gov/Sort_Public/OffenderSearchResults.aspx"

        data = {
            "ctl00_ContentPlaceHolder1_myScriptMgr_HiddenField": validation_values.ct100_placeholder_myscript_mgr,
            "__EVENTTARGET": f"ctl00$ContentPlaceHolder1$rptPager1$ctl{index}$lnkPage",
            "__EVENTARGUMENT": f"",
            "__VIEWSTATE": validation_values.view_state,
            "__VIEWSTATEGENERATOR": validation_values.view_generator_state,
            "ctl00_ContentPlaceHolder1_AddressMap_ClientState": validation_values.ct100_placeholder_address_map,
            "__VIEWSTATEENCRYPTED": validation_values.view_state_encrypted,
            "__EVENTVALIDATION": validation_values.event_validation,
            "ctl00$ContentPlaceHolder1$cpMap_ClientState": True,
            "ctl00$ContentPlaceHolder1$cpOffenders_ClientState": False
        }

        response = await self.post(url, data=data, follow_redirects=True)
        response.raise_for_status()

        if response.url == "https://state.sor.gbi.ga.gov/Sort_Public/ConditionsOfUse.aspx":
            logger.error("Captcha found, trying to solve..")
            captcha_html = await self.accept_conditions_of_use(validation_values)
            captcha_validation_values = await self.get_captcha_validation_values(captcha_html)

            captcha_text = await self.solve_captcha(captcha_validation_values.image_url)
            page_validation_values = await self.send_captcha_solution(captcha_text, captcha_validation_values)
            page_validation_values, first_page_html = await self.search_offenders(page_validation_values)
            logger.info("Captcha solved, continuing..")

            return await self.open_page(page_validation_values, index)

        return await self.get_page_validation_values(response.text)


    async def get_offender_details(self, validation_values: PageValidationValues, index: int) -> None:
        url = "https://state.sor.gbi.ga.gov/Sort_Public/OffenderSearchResults.aspx"

        data = {
            "ctl00_ContentPlaceHolder1_myScriptMgr_HiddenField": validation_values.ct100_placeholder_myscript_mgr,
            "__EVENTTARGET": "ctl00$ContentPlaceHolder1$grdSearchResults",
            "__EVENTARGUMENT": f"Select${index}",
            "__VIEWSTATE": validation_values.view_state,
            "__VIEWSTATEGENERATOR": validation_values.view_generator_state,
            "ctl00_ContentPlaceHolder1_AddressMap_ClientState": validation_values.ct100_placeholder_address_map,
            "__VIEWSTATEENCRYPTED": validation_values.view_state_encrypted,
            "__EVENTVALIDATION": validation_values.event_validation,
            "ctl00$ContentPlaceHolder1$cpMap_ClientState": True,
            "ctl00$ContentPlaceHolder1$cpOffenders_ClientState": False
        }

        response = await self.post(url, data=data, follow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")


        """FIRST NAME"""
        label_td_name = soup.find('td', class_='label', text='First Name')
        if label_td_name:
            first_name_td = label_td_name.find_next('td')
            first_name_value = first_name_td.text.strip() if first_name_td else None
        else:
            first_name_value = None


        """MIDDLE NAME"""
        label_td_middle_name = soup.find('td', class_='label', text='Middle Name')
        if label_td_middle_name:
            middle_name_td = label_td_middle_name.find_next('td')
            middle_name_value = middle_name_td.text.strip() if middle_name_td else None
        else:
            middle_name_value = None


        """LAST NAME"""
        label_td_last_name = soup.find('td', class_='label', text='Last Name')
        if label_td_last_name:
            last_name_td = label_td_last_name.find_next('td')
            last_name_value = last_name_td.text.strip() if last_name_td else None
        else:
            last_name_value = None



        """SUFFIX"""
        label_td_suffix = soup.find('td', class_='label', text='Suffix')
        if label_td_suffix:
            suffix_td = label_td_suffix.find_next('td')
            suffix_value = suffix_td.text.strip() if suffix_td else None
            suffix_value = suffix_value if suffix_value.strip() != '' else None
        else:
            suffix_value = None


        """ALIASES"""
        aliases_td = soup.find('td', style='color:Black;background-color:#E2E0D3; font-weight: bold;', text='Aliases:')
        if aliases_td:
            alias_divs = aliases_td.find_next('td').find_all('div')
            aliases_values = [div.text.strip() for div in alias_divs] if alias_divs else None
        else:
            aliases_values = None


        """GENDER/RACE/DATE OF BIRTH"""
        gender_race_yob_td = soup.find('td', style='color:Black;background-color:#E2E0D3; font-weight: bold;', text='Gender/Race/YOB:')
        if gender_race_yob_td:
            gender_tr = gender_race_yob_td.find_next('tr')
            race_tr = gender_tr.find_next('tr')
            yob_tr = race_tr.find_next('tr')

            gender_value = gender_tr.find('td', class_='label').find_next('td').text.strip() if gender_tr else None
            race_value = race_tr.find('td', class_='label').find_next('td').text.strip() if race_tr else None
            yob_value = yob_tr.find('td', class_='label').find_next('td').text.strip() if yob_tr else None

        else:
            gender_value = None
            race_value = None
            yob_value = None


        """ADDRESSES"""
        address_td = soup.find('td', style='color:Black;background-color:#E2E0D3; font-weight: bold;', text='Primary/Last Known Address:')
        if address_td:
            address_divs = address_td.find_next('td').find_all('div')

            address_lines = [div.text.strip() for div in address_divs] if address_divs else None
            if address_lines:
                addresses = ' '.join(address_lines)
            else:
                addresses = None
        else:
            addresses = None


        """HEIGHT"""
        height_element = soup.find('td', text='Height:')
        height = height_element.find_next_sibling('td').text if height_element else None


        """WEIGHT"""
        weight_element = soup.find('td', text='Weight:')
        weight = weight_element.find_next_sibling('td').text if weight_element else None


        """HAIR COLOR"""
        hair_color_element = soup.find('td', text='Hair Color:')
        hair_color = hair_color_element.find_next_sibling('td').text if hair_color_element else None


        """EYE COLOR"""
        eye_color_element = soup.find('td', text='Eye Color:')
        eye_color = eye_color_element.find_next_sibling('td').text if eye_color_element else None


        """STATUS INFO"""
        conviction_date_element = soup.find('td', {'style': 'width:100px;white-space:nowrap;'})
        conviction_date = conviction_date_element.text.strip() if conviction_date_element else None

        conviction_state_element = soup.find('td', {'style': 'width:150px;white-space:nowrap;'})
        conviction_state = conviction_state_element.text.strip() if conviction_state_element else None

        predator_element = soup.find('td', class_='label', text='Predator:')
        predator = predator_element.find_next('td').text.strip() if predator_element else None

        absconder_element = soup.find('td', class_='label', text='Absconder:')
        absconder = absconder_element.find_next('td').text.strip() if absconder_element else None

        registration_date_element = soup.find('td', class_='label', text='Registration Date:')
        registration_date = registration_date_element.find_next('td').text.strip() if registration_date_element else None

        residence_verification_date_element = soup.find('td', class_='label', text='Residence Verification Date:')
        residence_verification_date = residence_verification_date_element.find_next('td').text.strip() if residence_verification_date_element else None

        leveling_element = soup.find('td', class_='label', text='Leveling:')
        leveling = leveling_element.find_next('td').text.strip() if leveling_element else None


        """IMAGES"""
        all_image_elements = soup.find_all('img')
        image_links = [f"https://state.sor.gbi.ga.gov/Sort_Public/{img['src']}" for img in all_image_elements if 'src' in img.attrs and img["src"].startswith("DisplayImage.aspx")]

        if not image_links:
            image_links = None


        await OffendersData.add_offender(
            first_name=first_name_value,
            middle_name=middle_name_value,
            last_name=last_name_value,
            suffix=suffix_value,
            aliases=aliases_values,
            gender=gender_value,
            race=race_value,
            birth_date=yob_value,
            addresses=addresses,
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
            images=image_links
        )




    async def start(self) -> None:
        logger.info("Parser started..")

        try:
            condition_validation_values = await self.get_condition_validation_values()
            captcha_html = await self.accept_conditions_of_use(condition_validation_values)
            captcha_validation_values = await self.get_captcha_validation_values(captcha_html)

            captcha_text = await self.solve_captcha(captcha_validation_values.image_url)
            page_validation_values = await self.send_captcha_solution(captcha_text, captcha_validation_values)
            page_validation_values, first_page_html = await self.search_offenders(page_validation_values)

        except Exception as error:
            logger.error(f"Error while trying to setup session or solving captcha: {error}")
            input("Press any key to exit")
            sys.exit(1)


        for index in range(10):
            try:
                await self.get_offender_details(page_validation_values, index)
                logger.info(f"Got offender details for index: {index} | Start page")
            except Exception as error:
                logger.error(f"Error while trying to get offender details: {error} | First page")


        iteration_number = 0
        while True:
            if self.config["max_iterations"] < iteration_number:
                logger.success(f"Max iterations reached, exiting..")
                input("Press any key to exit")
                sys.exit(0)

            for page_index in range(10):
                source_page_index = f"0{page_index + 1}" if len(str(page_index + 1)) == 1 else str(page_index + 1)
                if iteration_number != 0:
                    source_page_index = f"0{page_index + 2}" if len(str(page_index + 2)) == 1 else str(page_index + 2)

                if source_page_index == "11":
                    source_page_index = "10"

                try:
                    page_validation_values = await self.open_page(page_validation_values, source_page_index)
                except Exception as error:
                    logger.error(f"Error while trying to open page: {error} | Page: {source_page_index} | Iteration number: {iteration_number}")
                    continue

                for index in range(10):
                    try:
                        await self.get_offender_details(page_validation_values, index)
                        logger.info(f"Got offender details for index: {index} | Page: {source_page_index} | Iteration number: {iteration_number}")

                    except Exception as error:
                        logger.error(f"Error while trying to get offender details: {error} | Page: {source_page_index} | Iteration number: {iteration_number}")

            iteration_number += 1
