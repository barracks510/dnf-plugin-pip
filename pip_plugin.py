# Copyright (c) 2017 Dennis Chen <barracks510@gmail.com

'''pip_plugin.py - DNF plugin to manipulate Python packages'''

from argparse import ArgumentParser, REMAINDER
from logging import getLogger
from sysconfig import get_python_version

from dnf import Plugin
from dnf.cli import Command, CliError
from dnf.cli.commands import err_mini_usage

from pip.download import PipSession
from pip.exceptions import InstallationError
from pip.req.req_file import parse_requirements
from pip.req.req_install import InstallRequirement

LOGGER = getLogger('dnf.plugin')


def make_parser(prog):
    '''ArgumentParser factory for pip subcommand'''

    parser = ArgumentParser(prog)
    parser.add_argument('--help-cmd', action='store_true')
    parser.add_argument('--python', default=get_python_version())
    subparsers = parser.add_subparsers(dest='action')

    install = subparsers.add_parser('install', help='install a package')
    install.add_argument(
        '-r',
        '--requirement',
        action='append',
        default=[],
        metavar='file')
    install.add_argument('pkgs', default=[], nargs=REMAINDER)

    uninstall = subparsers.add_parser('uninstall', help='uninstall a package')
    uninstall.add_argument(
        '-r',
        '--requirement',
        action='append',
        default=[],
        metavar='file')
    uninstall.add_argument('--autoremove', action='store_true', default=False)
    uninstall.add_argument('pkgs', default=[], nargs=REMAINDER)

    return parser


class PipPlugin(Plugin):
    name = 'pip'

    def __init__(self, base, cli):
        super(PipPlugin, self).__init__(base, cli)
        if cli:
            cli.register_command(PipCommand)


class PipCommand(Command):
    aliases = ('pip', 'pip3')
    summary = ('Search, download, and (un)install Python packages')

    def __init__(self, cli):
        super(PipCommand, self).__init__(cli)
        self.parser = None
        self.opts = None

    def _call_sub(self, name, *args):
        subfunc = getattr(self, name + '_' + self.opts.action, None)
        if callable(subfunc):
            subfunc(*args)

    def configure(self, args):
        self.opts = self.parse_args(args)
        self._call_sub('configure', args)

    def configure_help(self, args):
        pass

    def configure_install(self, args):
        self.cli.demands.root_user = True
        self.cli.demands.resolving = True
        self.cli.demands.available_repos = True
        self.cli.demands.sack_activation = True

    def configure_uninstall(self, args):
        self.cli.demands.root_user = True
        self.cli.demands.resolving = True
        self.cli.demands.available_repos = True
        self.cli.demands.sack_activation = True

    def parse_args(self, args):
        '''Returns parsed arguments'''
        self.parser = make_parser(self.aliases[0])
        opts = self.parser.parse_args(args)
        if opts.help_cmd:
            opts.action = 'help'
        elif not opts.action:
            err_mini_usage(self.cli, self.cli.base.basecmd)
            raise CliError
        return opts

    def process_request(self, callback):
        '''Scans all pypi packages and executes callback on each rpm equivilent'''
        session = PipSession()

        pip_reqs = []
        for filename in self.opts.requirement:
            try:
                file_reqs = parse_requirements(filename, session=session)
                pip_reqs.extend(file_reqs)
            except InstallationError as e:
                LOGGER.error('Error: %s', e)
                raise CliError
        for pkg in self.opts.pkgs:
            pkg_req = InstallRequirement.from_line(pkg)
            pip_reqs.append(pkg_req)

        if len(pip_reqs) == 0:
            LOGGER.error(
                'Error: Need to pass a list of pkgs to %s',
                self.opts.action)
            err_mini_usage(self.cli, self.cli.base.basecmd)
            raise CliError

        for pip_req in pip_reqs:
            name = pip_req.name
            cname = pip_req.name.lower()

            req = 'python%sdist(%s)' % (self.opts.python, cname)
            pkgs = self.base.sack.query().filter(provides=req).latest().run()
            if len(pkgs) == 0:
                LOGGER.error('WARNING: Could not find rpm for %s.', name)
            for pkg in pkgs:
                if pip_req.specifier.contains(pkg.v):
                    LOGGER.info(
                        'Package %s meets specifier \'%s%s\'.',
                        pkg, name, pip_req.specifier)
                    callback(pkg.name)

    def run(self, args):
        self._call_sub('run', args)

    def run_help(self, args):
        self.parser.print_help()

    def run_install(self, args):
        self.process_request(self.base.install)

    def run_uninstall(self, args):
        self.process_request(self.base.remove)
        if self.opts.autoremove:
            self.base.autoremove()
