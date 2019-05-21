import webbrowser
import bpy



def search_blenderscripting(input_string):
    try:
        search_string = 'http://blenderscripting.blogspot.com/search?q={}'
        webbrowser.open(search_string.format(input_string))
    except:
        print('unable to locate blenderscripting.blogspot.com')


def search_bpydocs(input_string):
    try:
        # https://docs.blender.org/api/blender_python_api_current/search.html
        s_head = 'https://docs.blender.org/api/blender_python_api_current/'
        s_slug = 'search.html?q='
        s_tail = '&check_keywords=yes&area=default'
        s_term = input_string
        webbrowser.open(''.join([s_head, s_slug, s_term, s_tail]))
    except:
        print('unable to browse docs online')


def search_pydocs(input_string):
    try:
        search_head = 'http://docs.python.org/3/search.html?q='
        search_tail = ''  # &check_keywords=yes&area=default'
        search_term = input_string
        webbrowser.open(''.join([search_head, search_term, search_tail]))
    except:
        print('unable to browse docs online')


def search_stack(input_string, site):
    try:
        search_string = 'http://' + site + '.com/search?q={}'
        input_string = input_string.replace(' ', '+')
        webbrowser.open(search_string.format(input_string))
        print('searching {0} for {1}'.format(site, input_string))
    except:
        print('unable to locate stachoverflow')


