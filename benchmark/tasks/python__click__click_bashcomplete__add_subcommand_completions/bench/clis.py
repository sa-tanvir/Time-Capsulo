"""Command trees used by the shell-completion bench drivers (modelled on click's test-suite)."""
import click

COLORS = ['red', 'green', 'blue', 'grey', 'black']


def _get_colors(ctx, args, incomplete):
    for c in COLORS:
        if c.startswith(incomplete):
            yield c


def _search_colors(ctx, args, incomplete):
    for c in COLORS:
        if incomplete in c:
            yield (c, 'colour ' + c)


def _complete(ctx, args, incomplete):
    return ['abc', 'def', 'ghi', 'jkl', 'mno', 'pqr', 'stu', 'vwx', 'yz']


def _noop(*a, **k):
    pass


def build_opts():
    @click.command()
    @click.option('--opt1', type=click.Choice(['opt11', 'opt12']), help='opt1 help')
    @click.option('--opt2', type=click.Choice(['opt21', 'opt22']), default='opt21')
    @click.option('--opt3', type=click.Choice(['opt', 'option']))
    @click.option('--message', '-m', multiple=True, type=click.Choice(['m1', 'm2']))
    @click.option('--shout/--no-shout', default=False, help='shout it')
    @click.option('--pos', nargs=2, type=click.Choice(['pos1', 'pos2']))
    @click.option('--secret', hidden=True, type=click.Choice([1, 2]))
    @click.argument('arg1', required=False, type=click.Choice(['arg11', 'arg12']))
    @click.argument('arg2', type=click.Choice(['arg21', 'arg22']), default='arg21')
    def cli(**kw):
        pass
    return cli


def build_chain():
    @click.group('cli', chain=True)
    @click.option('--cli-opt')
    @click.argument('arg', type=click.Choice(['cliarg1', 'cliarg2']))
    def cli(cli_opt, arg):
        pass

    @cli.command()
    @click.option('--asub-opt')
    def asub(asub_opt):
        pass

    @cli.command(help='bsub help')
    @click.option('--bsub-opt')
    @click.argument('arg', type=click.Choice(['arg1', 'arg2']))
    def bsub(bsub_opt, arg):
        pass

    @cli.command(short_help='the c command')
    @click.option('--csub-opt')
    @click.argument('arg', type=click.Choice(['carg1', 'carg2']), default='carg1')
    def csub(csub_opt, arg):
        pass

    @cli.command(hidden=True)
    def dsub():
        pass
    return cli


def build_long():
    @click.group('cli')
    @click.option('--cli-opt')
    def cli(cli_opt):
        pass

    @cli.group('asub')
    @click.option('--asub-opt')
    def asub(asub_opt):
        pass

    @asub.group('bsub', help='The b group.  It does b things.')
    @click.option('--bsub-opt')
    def bsub(bsub_opt):
        pass

    @bsub.command('csub')
    @click.option('--csub-opt', type=click.Choice(['foo', 'bar']))
    @click.option('--csub', type=click.Choice(['bar', 'baz']))
    @click.option('--search-color', autocompletion=_search_colors)
    @click.argument('color', autocompletion=_get_colors)
    def csub(**kw):
        pass

    @bsub.command('cother')
    @click.argument('things', nargs=-1, autocompletion=_complete)
    def cother(things):
        pass
    return cli


def build_longchoice():
    @click.group()
    def cli():
        pass

    @cli.group()
    @click.option('--sub-opt', type=click.Choice(['subopt1', 'subopt2']))
    @click.argument('sub-arg', required=False, type=click.Choice(['subarg1', 'subarg2']))
    def sub(sub_opt, sub_arg):
        pass

    @sub.command(short_help='bsub help')
    @click.option('--bsub-opt', type=click.Choice(['bsubopt1', 'bsubopt2']))
    @click.argument('bsub-arg1', required=False, type=click.Choice(['bsubarg1', 'bsubarg2']))
    @click.argument('bbsub-arg2', required=False, type=click.Choice(['bbsubarg1', 'bbsubarg2']))
    def bsub(**kw):
        pass

    @sub.group('csub')
    def csub():
        pass

    @csub.command()
    def dsub():
        pass

    @sub.group(chain=True)
    def esub():
        pass

    @esub.command()
    @click.option('-x', is_flag=True)
    def fsub(x):
        pass

    @esub.command()
    def gsub():
        pass
    return cli


def build_hidden():
    @click.group()
    @click.option('--name', hidden=True)
    @click.option('--choices', type=click.Choice([1, 2]), hidden=True)
    @click.option('--verbose', '-v', count=True)
    def cli(**kw):
        pass

    @cli.group(hidden=True)
    def hgroup():
        pass

    @hgroup.group()
    def hgroupsub():
        pass

    @cli.command()
    def asub():
        pass

    @cli.command(hidden=True)
    @click.option('--hname')
    def hsub(hname):
        pass
    return cli


def build_variadic():
    @click.group()
    def entrypoint():
        pass

    @click.command()
    @click.option('--opt', autocompletion=_complete)
    @click.argument('arg', nargs=-1)
    def subcommand(opt, arg):
        pass

    @click.command()
    @click.option('--opt', type=click.Choice(['opt1', 'opt2']))
    @click.argument('src', nargs=-1, type=click.Choice(['src1', 'src2']))
    def files(opt, src):
        pass

    entrypoint.add_command(subcommand)
    entrypoint.add_command(files)
    return entrypoint


SYLL = ['ba', 'ce', 'di', 'fo', 'gu', 'ka', 'le', 'mi', 'no', 'pu']
HELPS = [None, 'Short help.', 'Run the thing.  Then do more things after that.',
         'This is a long text that is too long to show as short help and will be truncated instead.',
         'Login and store the token in ~/.netrc.']


def _add_many(group, n, offset):
    for k in range(n):
        name = SYLL[(k + offset) % 10] + SYLL[(k // 10) % 10] + str(k // 100)
        kw = {'help': HELPS[(k + offset) % len(HELPS)], 'hidden': (k + offset) % 9 == 0}
        if (k + offset) % 5 == 0:
            kw['short_help'] = 'short ' + name
        group.add_command(click.Command(name, callback=_noop, **kw))


def build_big(n=40):
    """Large tree; every group holds about `n` subcommands."""
    root = click.Group('root')
    _add_many(root, n, 1)
    pipe = click.Group('pipe', chain=True, help='Chained pipeline.')
    _add_many(pipe, n, 3)
    root.add_command(pipe)
    nested = click.Group('nested')
    inner = click.Group('inner', chain=True)
    _add_many(inner, n, 5)
    nested.add_command(inner)
    _add_many(nested, max(1, n // 4), 7)
    root.add_command(nested)
    return root


BUILDERS = {'opts': build_opts, 'chain': build_chain, 'long': build_long,
            'longchoice': build_longchoice, 'hidden': build_hidden, 'variadic': build_variadic, 'big': build_big}


def build_all():
    return {k: f() for k, f in BUILDERS.items()}
