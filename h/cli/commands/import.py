# -*- coding: utf-8 -*-

import click
import json

from h.schemas.annotation_import import AnnotationImportSchema


@click.command('import')
@click.argument('annotation_file', type=click.File('rb'))
def import_annotations(annotation_file):

    with annotation_file:
        raw_annotations = json.load(annotation_file)

    click.echo('{} annotations to import'.format(len(raw_annotations)))

    schema = AnnotationImportSchema()

    [schema.validate(ann) for ann in raw_annotations]