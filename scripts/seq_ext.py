#!/usr/bin/env python

import argparse
import sys
import logging
import os.path as pt
import pandas as pd
import progressbar
import warnings

from predict import seq_ext


class App(object):

    def run(self, args):
        name = pt.basename(args[0])
        parser = self.create_parser(name)
        opts = parser.parse_args(args[1:])
        return self.main(name, opts)

    def create_parser(self, name):
        p = argparse.ArgumentParser(
            prog=name,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='Extracts sequence windows over positions')
        p.add_argument(
            'seq_file',
            help='HDF path to chromosome sequences')
        p.add_argument(
            'pos_file',
            help='Position file with pos and chromo column')
        p.add_argument(
            '-o', '--out_file',
            help='Output HDF path')
        p.add_argument(
            '--wlen',
            help='Length of sequence window at positions',
            default=101,
            type=int)
        p.add_argument(
            '--chromos',
            help='Only apply to these chromosome',
            nargs='+')
        p.add_argument(
            '--start',
            help='Start position on chromosome',
            type=int)
        p.add_argument(
            '--stop',
            help='Stop position on chromosome',
            type=int)
        p.add_argument(
            '--verbose', help='More detailed log messages', action='store_true')
        p.add_argument(
            '--log_file', help='Write log messages to file')
        return p

    def main(self, name, opts):
        logging.basicConfig(filename=opts.log_file,
                            format='%(levelname)s (%(asctime)s): %(message)s')
        log = logging.getLogger(name)
        if opts.verbose:
            log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.INFO)
        log.debug(opts)

        log.info('Read positions ...')
        pos = pd.read_table(opts.pos_file, dtype={'chromo': str})
        if opts.chromos is not None:
            pos = pos.loc[pos.chromo.isin(opts.chromos)]
        if opts.start is not None:
            pos = pos.loc[pos.pos >= opts.start]
        if opts.stop is not None:
            pos = pos.loc[pos.pos <= opts.stop]
        pos.sort(['chromo', 'pos'], inplace=True)

        proc = seq_ext.Processor(opts.wlen)
        proc.progbar = progressbar.ProgressBar(term_width=80)
        proc.logger = lambda x: log.info(x)
        log.info('Process ...')
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            proc.process(opts.seq_file, pos, opts.out_file)

        log.info('Done!')
        return 0


if __name__ == '__main__':
    app = App()
    app.run(sys.argv)