
x = input('Input "c" for CTP Demo, else for IB Demo!\n')
if x == 'c':
    from .run_ctp import main
else:
    from .run_ib import main

# from .run import main

if __name__ == "__main__":
    main()
