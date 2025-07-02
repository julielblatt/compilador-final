def print_ast(node, indent=0):
    espaco = '  ' * indent
    if isinstance(node, list):
        print(f"{espaco}[")
        for item in node:
            print_ast(item, indent + 1)
        print(f"{espaco}]")
    elif isinstance(node, (int, str)):
        print(f"{espaco}{repr(node)}")
    elif hasattr(node, '__dict__'):
        print(f"{espaco}{node.__class__.__name__}")
        for attr in vars(node):
            valor = getattr(node, attr)
            print(f"{espaco}  .{attr}:")
            print_ast(valor, indent + 2)
    else:
        print(f"{espaco}{repr(node)}")
