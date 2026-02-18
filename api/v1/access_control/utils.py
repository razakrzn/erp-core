import re
from django.urls import get_resolver

def simplify_pattern(path):
    """
    Clean up regex characters from URL patterns to make them user-friendly.
    """
    # Remove start/end regex markers
    path = path.replace('^', '').replace('$', '')
    
    # Remove optional format suffix (e.g. \.(?P<format>[a-z0-9]+)/?)
    # This regex matches the DRF format suffix pattern
    path = re.sub(r'\\\.\(\?P<format>\[a-z0-9\]\+\)/\??', '', path)
    
    # Handle named groups (?P<name>pattern) -> <name>
    path = re.sub(r'\(\?P<([^>]+)>[^)]+\)', r'<\1>', path)
    
    # Remove <drf_format_suffix:format> placeholder
    path = path.replace('<drf_format_suffix:format>', '')
    
    # Clean up escaped dots
    path = path.replace('\\.', '.')
    
    # Normalize slashes (remove double slashes if any)
    path = path.replace('//', '/')
    
    # Ensure trailing slash
    if not path.endswith('/'):
        path += '/'
    
    # Ensure leading slash
    if not path.startswith('/'):
        path = '/' + path
    
    return path

def get_all_url_patterns(patterns=None, prefix=''):
    if patterns is None:
        resolver = get_resolver()
        patterns = resolver.url_patterns

    url_list = []
    for pattern in patterns:
        if hasattr(pattern, 'url_patterns'):
            # It's a resolver (include), recurse
            new_prefix = prefix + str(pattern.pattern)
            url_list.extend(get_all_url_patterns(pattern.url_patterns, new_prefix))
        else:
            # It's a pattern
            raw_path = prefix + str(pattern.pattern)
            path = simplify_pattern(raw_path)
            
            methods = []
            if hasattr(pattern, 'callback'):
                view = pattern.callback
                if hasattr(view, 'cls'):
                    # It's a class-based view (likely DRF)
                    if hasattr(view, 'actions'):
                        # ViewSet actions mapping
                        methods = list(view.actions.keys())
                    elif hasattr(view.cls, 'http_method_names'):
                        # APIView or standard View
                        methods = view.cls.http_method_names
                else:
                    # Function-based view
                    methods = ['GET'] 
            
            # Normalize methods to upper case
            methods = [m.upper() for m in methods if m.lower() in ['get', 'post', 'put', 'patch', 'delete']]
            
            # Only include if methods exist and path is not empty
            if methods and path: 
                url_list.append({'path': path, 'methods': sorted(list(set(methods)))})
    return url_list
