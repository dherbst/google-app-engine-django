import os
from django.core.management.base import NoArgsCommand
from optparse import make_option

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--plain', action='store_true', dest='plain',
            help='Tells Django to use plain Python, not IPython.'),
        make_option('--datastore_path', type='string', nargs=1, dest='datastore_path',
                    help='Specify location of the datastore file for GAE'),
        make_option('--history_path', type='string', nargs=1, dest='history_path',
                    help='Specify the location of the history file for GAE'),
        make_option('--blobstore_path', type='string', nargs=1, dest='blogstore_path',
                    help='Specify the location of the blobstore for GAE'),
    )
    help = "Runs a Python interactive interpreter. Tries to use IPython, if it's available."

    requires_model_validation = False

    def handle_noargs(self, **options):
        # XXX: (Temporary) workaround for ticket #1796: force early loading of all
        # models from installed apps.
        from django.db.models.loading import get_models
        loaded_models = get_models()

        use_plain = options.get('plain', False)

        datastore_path = options.get('datastore_path', None)
        history_path = options.get('history_path', None)
        blobstore_path = options.get('blobstore_path', None)
        from google.appengine.tools import dev_appserver_main
        must_setup = False
        if datastore_path:
            dev_appserver_main.DEFAULT_ARGS['datastore_path'] = datastore_path
            must_setup = True
        if history_path:
            dev_appserver_main.DEFAULT_ARGS['history_path'] = history_path
            must_setup = True
        if blobstore_path:
            dev_appserver_main.DEFAULT_ARGS['blobstore_path'] = blobstore_path
            must_setup = True

        if must_setup:
            from appengine_django import appid
            from google.appengine.tools import dev_appserver
            args = dev_appserver_main.DEFAULT_ARGS.copy()
            dev_appserver.SetupStubs(appid, **args)

        try:
            if use_plain:
                # Don't bother loading IPython, because the user wants plain Python.
                raise ImportError
            import IPython
            # Explicitly pass an empty list as arguments, because otherwise IPython
            # would use sys.argv from this script.
            shell = IPython.Shell.IPShell(argv=[])
            shell.mainloop()
        except ImportError:
            import code
            # Set up a dictionary to serve as the environment for the shell, so
            # that tab completion works on objects that are imported at runtime.
            # See ticket 5082.
            imported_objects = {}
            try: # Try activating rlcompleter, because it's handy.
                import readline
            except ImportError:
                pass
            else:
                # We don't have to wrap the following import in a 'try', because
                # we already know 'readline' was imported successfully.
                import rlcompleter
                readline.set_completer(rlcompleter.Completer(imported_objects).complete)
                readline.parse_and_bind("tab:complete")

            # We want to honor both $PYTHONSTARTUP and .pythonrc.py, so follow system
            # conventions and get $PYTHONSTARTUP first then import user.
            if not use_plain: 
                pythonrc = os.environ.get("PYTHONSTARTUP") 
                if pythonrc and os.path.isfile(pythonrc): 
                    try: 
                        execfile(pythonrc) 
                    except NameError: 
                        pass
                # This will import .pythonrc.py as a side-effect
                import user
            code.interact(local=imported_objects)
