import argparse
import cv2
import numpy as np
import pyautogui
import time


def get_screen_scaling():
    actual_width, actual_height = pyautogui.size()
    ss = pyautogui.screenshot()
    origin_width, origin_height = ss.size
    s = origin_width / actual_width
    print("Actual screen resolution: {}x{}".format(actual_width, actual_height))
    print("Origin screen resolution: {}x{}".format(origin_width, origin_height))
    print("Scaling is: {}".format(s))
    return s


SCALING = get_screen_scaling()


def process_instructions(inputs):
    instructions = []
    images = []
    will_collect_images = False
    for input in inputs:
        if input.startswith("--image"):
            will_collect_images = True
            continue
        if input.startswith("--"):
            will_collect_images = False
            if len(images):
                instructions.append(images)
            continue
        if will_collect_images:
            images.append(input)
        else:
            instructions.append(input)
    print("Processed instructions: ", instructions)
    return instructions


def search(template_paths, timeout=30, interval=1, scaling: int = SCALING):
    wait(1)
    print("Search for templates {}".format(template_paths))
    templates = []
    for template_path in template_paths:
        templates.append(cv2.imread(template_path, cv2.IMREAD_GRAYSCALE))
    start = time.time()
    elapsed = time.time() - start
    click_points = []
    while elapsed < timeout:
        screenshot = pyautogui.screenshot()
        screenshot = np.array(screenshot)
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        results = []
        for template in templates:
            results.append(cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED))

        threshold = 0.9

        for result in results:
            locations = np.where(result >= threshold)
            for pt in zip(*locations[::-1]):
                center_x = pt[0] + template.shape[1] // 2
                center_y = pt[1] + template.shape[0] // 2
                click_points.append([center_x // scaling, center_y // scaling])
                print("Found click point: {}px, {}px".format(*click_points[-1]))

        if len(click_points) == 0:
            print(
                "No click point found, keep looking {}s...".format(
                    round(elapsed - timeout)
                )
            )
        else:
            return click_points

        time.sleep(interval)
        elapsed = time.time() - start
    print("No click point found, timeout!!!")
    return click_points


def search_and_click(*args, timeout: int = 30, double_click: bool):
    click_points = search(*args, timeout=timeout)
    if len(click_points) >= 1:
        print("Click cursor to point {}".format(click_points[0]))
        if double_click:
            pyautogui.doubleClick(click_points[0])
        else:
            pyautogui.click(click_points[0])
    return len(click_points) >= 1


def search_and_click_all(*args, timeout: int = 30, double_click: bool):
    click_points = search(*args, timeout=timeout)
    for cp_idx, cp in enumerate(click_points):
        print("Click cursor to point {} {}".format(cp_idx, cp))
        if double_click:
            pyautogui.doubleClick(cp)
        else:
            pyautogui.click(cp)
        time.sleep(1)
    return len(click_points) >= 1


def click(*args, **kwargs):
    return pyautogui.click(*args, **kwargs)


def db_click(*args, **kwargs):
    return pyautogui.doubleClick(*args, **kwargs)


def typing(*args, **kwargs):
    return pyautogui.typewrite(*args, **kwargs)


def pressing(*args, **kwargs):
    return pyautogui.press(*args, **kwargs)


def wait(*args, **kwargs):
    return time.sleep(*args, **kwargs)


def perform_action(project, command, command_args):
    if command == "search":
        return search(
            list(map(lambda p: project + "/images/" + p, command_args[0])),
            timeout=int(command_args[1]),
        )
    if command == "search_and_click":
        return search_and_click(
            list(map(lambda p: project + "/images/" + p, command_args[0])),
            timeout=int(command_args[1]),
            double_click=False,
        )
    if command == "search_and_double_click":
        return search_and_click(
            list(map(lambda p: project + "/images/" + p, command_args[0])),
            timeout=int(command_args[1]),
            double_click=True,
        )
    if command == "wait":
        print("Wait for {}s".format(command_args[0]))
        return wait(int(command_args[0]))
    if command == "click":
        print("Force click {}".format(command_args))
        return click(int(command_args[0]), int(command_args[1]))
    if command == "double_click":
        print("Force db click {}".format(command_args))
        return db_click(int(command_args[0]), int(command_args[1]))
    if command == "typing":
        print("Typing {}".format(command_args[0]))
        return typing(command_args[0])
    if command == "pressing":
        print("Pressing {}".format(command_args))
        return pressing(*command_args)


def page_main(project, profiles):
    ps = []
    with open(profiles + ".txt", "r") as file:
        for line in file:
            if line.strip() != "" and not line.startswith("#"):
                ps.append(line.strip())

    print("Profiles: {}".format(ps))

    for p_idx, p in enumerate(ps):
        print("Now start profile {} from name {}".format(p_idx, p))
        wait(0.25)
        if not search_and_click(["morelogin_logo.png"], timeout=10, double_click=True):
            continue
        wait(0.25)
        if not search_and_click(["profile_filter.png"], timeout=10, double_click=False):
            continue
        wait(1)
        if not search_and_click(
            ["profile_filter_reset.png"], timeout=10, double_click=False
        ):
            continue
        wait(0.5)
        if not search_and_click(
            ["profile_enter_name.png"], timeout=10, double_click=False
        ):
            continue
        wait(0.25)
        typing(p)
        if not search_and_click(
            ["profile_filter_ok.png"], timeout=5, double_click=False
        ):
            continue
        wait(2)

        if not search_and_click(["profile_start.png"], timeout=20, double_click=True):
            continue

        with open(project + "/plot.txt", "r") as file:
            for line in file:
                if line.strip() != "" and not line.startswith("#"):
                    instructions = process_instructions(line.strip().split(" "))
                    command = instructions[0]
                    command_args = instructions[1:]
                    perform_action(project, command, command_args)
        wait(1)
        search_and_click(["profile_close.png"], timeout=10, double_click=False)
        wait(1.5)


def page_scroll():
    wait(3)
    pyautogui.moveTo(450, 250)
    wait(1)
    pyautogui.click(450, 250)
    wait(1)
    pyautogui.scroll(-821, x=450, y=250)


def main():
    parser = argparse.ArgumentParser(
        description="UP s automation for search and interact by pixels"
    )
    parser.add_argument(
        "--test", action="store_true", required=False, help="Select project folder"
    )
    parser.add_argument(
        "--project", type=str, required=True, help="Select project folder"
    )
    parser.add_argument(
        "--profiles", type=str, required=True, help="Only use a number of profiles"
    )
    args = parser.parse_args()
    test = args.test
    project = args.project
    profiles = args.profiles

    if test:
        return

    page_main(project, profiles)


main()
