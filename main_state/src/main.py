import asyncio
import base64
import uuid
import aiofiles

from bs4 import BeautifulSoup
from loguru import logger

from src.captcha import Captcha
from database import *

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, Page


class Parser:
    def __init__(self, config: dict, thread_id: int):
        super().__init__()

        self.config: dict = config
        self.thread_id: int = thread_id


    async def solve_captcha(self, image_data: str) -> str:
        """Solve captcha using 2Captcha service"""

        async with aiofiles.open(f"./temp/{image_data}", 'rb') as f:
            result = await Captcha(
                image_data=str(base64.b64encode(await f.read()), "utf-8"),
                api_key=self.config["two_captcha_api_key"],
            ).solve()

        return result



    async def get_offender_details_with_browser(self, html: str, page: Page) -> bool:
        try:
            await page.wait_for_url("https://state.sor.gbi.ga.gov/Sort_Public/OffenderDetails.aspx", timeout=10000, wait_until="load")
            soup = BeautifulSoup(html, "html.parser")


            """FIRST NAME"""
            label_td_name = soup.find('td', class_='label', text='First Name')
            if label_td_name:
                first_name_td = label_td_name.find_next('td') if label_td_name else None
                first_name_value = first_name_td.text.strip() if first_name_td else None
            else:
                first_name_value = None


            """MIDDLE NAME"""
            label_td_middle_name = soup.find('td', class_='label', text='Middle Name')
            if label_td_middle_name:
                middle_name_td = label_td_middle_name.find_next('td') if label_td_middle_name else None
                middle_name_value = middle_name_td.text.strip() if middle_name_td else None
            else:
                middle_name_value = None


            """LAST NAME"""
            label_td_last_name = soup.find('td', class_='label', text='Last Name')
            if label_td_last_name:
                last_name_td = label_td_last_name.find_next('td') if label_td_last_name else None
                last_name_value = last_name_td.text.strip() if last_name_td else None
            else:
                last_name_value = None



            """SUFFIX"""
            label_td_suffix = soup.find('td', class_='label', text='Suffix')
            if label_td_suffix:
                suffix_td = label_td_suffix.find_next('td') if label_td_suffix else None
                suffix_value = suffix_td.text.strip() if suffix_td else None
                suffix_value = suffix_value if suffix_value.strip() != '' else None
            else:
                suffix_value = None


            """ALIASES"""
            aliases_td = soup.find('td', style='color:Black;background-color:#E2E0D3; font-weight: bold;', text='Aliases:')
            if aliases_td:
                alias_divs = aliases_td.find_next('td').find_all('div') if aliases_td else None
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
                address_divs = address_td.find_next('td').find_all('div') if address_td else None

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

            await page.click("#ctl00_ContentPlaceHolder1_lnkResults")  # Go back to search results
            await page.wait_for_url("https://state.sor.gbi.ga.gov/Sort_Public/OffenderSearchResults.aspx", timeout=10000, wait_until="load")

            return await OffendersData.add_offender(
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

        except Exception as error:
            if not await self.close_alias_window(page):
                logger.error(f"Error while parsing offender details: {error}")


            if page.url == "https://state.sor.gbi.ga.gov/Sort_Public/OffenderDetails.aspx":
                await page.click("#ctl00_ContentPlaceHolder1_lnkResults")  # Go back to search results
                await page.wait_for_url("https://state.sor.gbi.ga.gov/Sort_Public/OffenderSearchResults.aspx", timeout=10000, wait_until="load")


    @staticmethod
    async def close_alias_window(page: Page) -> bool:
        for page in page.context.pages:
            if page.url.startswith("https://state.sor.gbi.ga.gov/Alias.aspx"):
                logger.info("Alias page found, closing..")
                await page.close()
                return True

        return False



    async def accept_conditions_of_use_with_browser(self, page: Page):
        try:
            element = await page.wait_for_selector("#ctl00_ContentPlaceHolder1_btnAgree", timeout=10000)
            await element.click()
            await page.wait_for_url("https://state.sor.gbi.ga.gov/Sort_Public/Captcha.aspx", timeout=10000, wait_until="load")

        except PlaywrightTimeoutError:
            logger.error(f"Thread: {self.thread_id} | Can't find agree button")
            await self.validate_page_for_parsing(page)


    @staticmethod
    async def send_captcha_solution_with_browser(captcha_solution: str, page: Page) -> bool:
        try:
            await page.wait_for_selector("#ctl00_ContentPlaceHolder1_CodeTextBox", timeout=10000)
            await page.fill("#ctl00_ContentPlaceHolder1_CodeTextBox", captcha_solution)
            await asyncio.sleep(1)
            await page.click("#ctl00_ContentPlaceHolder1_ValidateButton")
            await page.wait_for_url("https://state.sor.gbi.ga.gov/Sort_Public/SearchOffender.aspx", timeout=5000, wait_until="load")
            return True

        except PlaywrightTimeoutError:
            return False


    async def get_captcha_image_with_browser(self, page: Page) -> str:
        try:
            await page.wait_for_selector("#captcha_ctl00_contentplaceholder1_botdetectcaptcha_CaptchaImage", timeout=10000)
            captcha_image_element = await page.query_selector("#captcha_ctl00_contentplaceholder1_botdetectcaptcha_CaptchaImage")

            image_name = f"{uuid.uuid4()}_captcha.jpeg"
            await captcha_image_element.screenshot(path=f"./temp/{image_name}")
            await asyncio.sleep(1)

            return image_name

        except PlaywrightTimeoutError:
            logger.error(f"Thread: {self.thread_id} | Can't find captcha image element")
            await self.validate_page_for_parsing(page)


    async def search_offenders_with_browser(self, page: Page):
        try:
            element = await page.wait_for_selector("#ctl00_ContentPlaceHolder1_btnSearch", timeout=10000)
            await element.click()
            await page.wait_for_url("https://state.sor.gbi.ga.gov/Sort_Public/OffenderSearchResults.aspx", timeout=10000, wait_until="load")

        except PlaywrightTimeoutError:
            await self.validate_page_for_parsing(page)


    async def get_offenders_with_browser(self, page: Page):
        try:
            element = await page.wait_for_selector("#ctl00_ContentPlaceHolder1_grdSearchResults", timeout=10000)
            return await element.query_selector_all("a")

        except PlaywrightTimeoutError:
            await self.validate_page_for_parsing(page)


    @staticmethod
    async def open_next_block_of_pages(page: Page) -> bool:
        try:
            element = await page.wait_for_selector("#ctl00_ContentPlaceHolder1_rptPager_ctl10_lnkPage", timeout=10000)
            await element.click()
            await page.wait_for_url("https://state.sor.gbi.ga.gov/Sort_Public/OffenderSearchResults.aspx", timeout=10000, wait_until="load")
            return True

        except PlaywrightTimeoutError:
            return False


    async def open_new_page_with_browser(self, page: Page, index: int):
        try:
            selector = f"#ctl00_ContentPlaceHolder1_rptPager_ctl0{index}_lnkPage" if index < 10 else f"#ctl00_ContentPlaceHolder1_rptPager_ctl{index}_lnkPage"

            element = await page.wait_for_selector(selector, timeout=10000)
            await element.click(timeout=10000)
            await page.wait_for_url("https://state.sor.gbi.ga.gov/Sort_Public/OffenderSearchResults.aspx", timeout=10000, wait_until="load")

        except PlaywrightTimeoutError:
            await self.open_new_page_with_browser(page, index + 1)



    async def validate_page_for_parsing(self, page: Page):
        await page.wait_for_timeout(1000)

        if page.url == "https://state.sor.gbi.ga.gov/Sort_Public/Captcha.aspx":
            logger.info(f"Thread: {self.thread_id} | Captcha found, trying to solve..")
            captcha_filename = await self.get_captcha_image_with_browser(page)
            captcha_text = await self.solve_captcha(captcha_filename)

            if await self.send_captcha_solution_with_browser(captcha_text, page):
                logger.info(f"Thread: {self.thread_id} | Captcha solved, continuing..")
                await self.validate_page_for_parsing(page)
            else:
                logger.error(f"Thread: {self.thread_id} | Captcha solution is wrong, trying again..")
                await page.reload(wait_until="load")
                await self.validate_page_for_parsing(page)


        elif page.url in ("https://state.sor.gbi.ga.gov/Sort_Public/ConditionsOfUse.aspx", "https://state.sor.gbi.ga.gov/Sort_Public/"):
            logger.info(f"Thread: {self.thread_id} | Conditions of use found, trying to accept..")
            await self.accept_conditions_of_use_with_browser(page)
            await self.validate_page_for_parsing(page)


        elif page.url == "https://state.sor.gbi.ga.gov/Sort_Public/SearchOffender.aspx":
            logger.info(f"Thread: {self.thread_id} | Search offender page found, trying to search..")
            await self.search_offenders_with_browser(page)
            await self.validate_page_for_parsing(page)



    async def start_with_browser(self):
        logger.info(f"Thread: {self.thread_id} | Parser started..")

        async with async_playwright() as pw:
            try:
                browser = await pw.chromium.launch(headless=False)
                context = await browser.new_context()
                page = await context.new_page()
                await page.goto("https://state.sor.gbi.ga.gov/Sort_Public/", wait_until="load")
                await self.validate_page_for_parsing(page)

            except Exception as error:
                logger.error(f"Thread: {self.thread_id} | Error while trying to start browser: {error}")
                return

            while True:
                first_page_in_block = False

                # Pages (1-10)
                for page_index in range(1, 11):
                    # Open new page if not first page in block
                    if not first_page_in_block and page_index != 1:
                        try:
                            await self.open_new_page_with_browser(page, page_index)

                        except Exception as error:
                            logger.error(f"Thread: {self.thread_id} | Error while trying to open page: {error}")
                            await self.validate_page_for_parsing(page)
                            continue

                    # Offenders (1-10) on page
                    for offender_index in range(10):
                        try:
                            offenders = await self.get_offenders_with_browser(page)
                            await offenders[offender_index].scroll_into_view_if_needed(timeout=10000)
                            await offenders[offender_index].click(timeout=10000)

                            # If offender exists (True) - open next block of pages, else - continue
                            status = await self.get_offender_details_with_browser(await page.content(), page)
                            if status:
                                if not await self.open_next_block_of_pages(page):
                                    logger.success(f"Thread: {self.thread_id} | All offenders parsed")
                                    await browser.close()
                                    await pw.stop()
                                    return

                                first_page_in_block = True
                                break

                            first_page_in_block = False

                        except Exception as error:
                            logger.error(f"Thread: {self.thread_id} | Error while trying to get offender details: {error}")
                            await self.validate_page_for_parsing(page)
