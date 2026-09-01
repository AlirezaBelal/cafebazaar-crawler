import traceback
from time import sleep

import bazarService

import config

print(" == START FETCHING CATEGORIES == ")
categories = bazarService.get_cafebazaar_categories()
for category in categories:
    print(" == START FETCHING SUBCATEGORIES OF " + category["title"] + "== ")
    sub_categories = bazarService.fetch_all_subcategories(category["path"])
    for sub_category in sub_categories:
        config.DEVICE_ID = config.generate_random_string()
        print(" == START FETCHING APP LIST OF " + sub_category["title"] + "== ")
        apps = bazarService.fetch_all_apps(sub_category["path"])
        for app in apps:
            try:
                app_detail = bazarService.fetch_app_details(app["packageName"], sub_category["title"])
                print(" == INFO OF " + app_detail.package_name + " IS FETCHED == ")
                # append_dict_to_file(config.RESULT_FILE, app_detail)
            except Exception as e:
                print(e)
                traceback.print_exc()
            sleep(config.SLEEP_AFTER_EACH_APPS_IN_MILL_SECONDS / 1000)
        sleep(config.SLEEP_AFTER_EACH_SUB_CATEGORIES_IN_MILL_SECONDS / 1000)
    sleep(config.SLEEP_AFTER_EACH_CATEGORIES_IN_MILL_SECONDS / 1000)
