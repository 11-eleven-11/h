# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import mock
import pytest

from memex.interfaces import IGroupService

from h.services.annotation_json_presentation import AnnotationJSONPresentationService
from h.services.annotation_json_presentation import annotation_json_presentation_service_factory
from h.presenters import AnnotationJSONPresenter


@pytest.mark.usefixtures('presenters')
class TestAnnotationJSONPresentationService(object):
    def test_present_gets_presenter(self, svc, patch, annotation_resource):
        get_presenter = patch('h.services.annotation_json_presentation.AnnotationJSONPresentationService.get_presenter')

        svc.present(annotation_resource)

        get_presenter.assert_called_once_with(svc, annotation_resource)

    def test_present_returns_presenter_dict(self, svc, presenters):
        presenter = presenters.AnnotationJSONPresenter.return_value

        result = svc.present(mock.Mock())

        assert result == presenter.asdict.return_value

    def test_present_all_loads_annotations_from_db(self, svc, storage):
        svc.present_all(['id-1', 'id-2'])

        storage.fetch_ordered_annotations.assert_called_once_with(
            svc.session, ['id-1', 'id-2'], query_processor=mock.ANY)

    def test_present_all_initialises_annotation_resources(self, svc, storage, resources):
        ann = mock.Mock()
        storage.fetch_ordered_annotations.return_value = [ann]

        svc.present_all(['ann-1'])

        resources.AnnotationResource.assert_called_once_with(ann, svc.group_svc, svc.links_svc)

    def test_present_all_presents_annotation_resources(self, svc, storage, resources, present):
        storage.fetch_ordered_annotations.return_value = [mock.Mock()]
        resource = resources.AnnotationResource.return_value

        svc.present_all(['ann-1'])
        present.assert_called_once_with(svc, resource)

    def test_present_all_preloads_formatters(self, svc, storage):
        formatter = mock.Mock(spec_set=['preload'])
        svc.formatters = [formatter]

        svc.present_all(['ann-1', 'ann-2'])

        formatter.preload.assert_called_once_with(['ann-1', 'ann-2'])

    def test_returns_presented_annotations(self, svc, storage, present):
        storage.fetch_ordered_annotations.return_value = [mock.Mock()]

        result = svc.present_all(['ann-1'])
        assert result == [present.return_value]

    def test_get_presenter_inits_presenter(self, svc, presenters, annotation_resource):
        svc.get_presenter(annotation_resource)

        presenters.AnnotationJSONPresenter.assert_called_once_with(annotation_resource)

    def test_get_presenter_returns_presenter(self, svc):
        resource = mock.Mock()

        result = svc.get_presenter(resource)
        assert isinstance(result, AnnotationJSONPresenter)

    def test_get_presenter_adds_formatters(self, svc, annotation_resource, presenters):
        formatters = [mock.Mock(), mock.Mock()]
        svc.formatters = formatters
        presenter = presenters.AnnotationJSONPresenter.return_value

        svc.get_presenter(annotation_resource)

        assert presenter.add_formatter.mock_calls == [mock.call(f) for f in formatters]

    @pytest.fixture
    def svc(self, db_session):
        group_svc = mock.Mock()
        links_svc = mock.Mock()
        return AnnotationJSONPresentationService(db_session, group_svc, links_svc)

    @pytest.fixture
    def annotation_resource(self):
        return mock.Mock(spec_set=['annotation'], annotation=mock.Mock())

    @pytest.fixture
    def presenters(self, patch):
        return patch('h.services.annotation_json_presentation.presenters')

    @pytest.fixture
    def storage(self, patch):
        return patch('h.services.annotation_json_presentation.storage')

    @pytest.fixture
    def resources(self, patch):
        return patch('h.services.annotation_json_presentation.resources')

    @pytest.fixture
    def present(self, patch):
        return patch('h.services.annotation_json_presentation.AnnotationJSONPresentationService.present')


@pytest.mark.usefixtures('group_svc', 'links_svc')
class TestAnnotationJSONPresentationServiceFactory(object):
    def test_returns_service(self, pyramid_request):
        svc = annotation_json_presentation_service_factory(None, pyramid_request)

        assert isinstance(svc, AnnotationJSONPresentationService)

    def test_provides_session(self, pyramid_request):
        svc = annotation_json_presentation_service_factory(None, pyramid_request)

        assert svc.session == pyramid_request.db

    def test_provides_group_service(self, pyramid_request, group_svc):
        svc = annotation_json_presentation_service_factory(None, pyramid_request)

        assert svc.group_svc == group_svc

    def test_passes_links_service(self, pyramid_request, links_svc):
        svc = annotation_json_presentation_service_factory(None, pyramid_request)

        assert svc.links_svc == links_svc

    @pytest.fixture
    def group_svc(self, pyramid_config):
        svc = mock.Mock()
        pyramid_config.register_service(svc, iface=IGroupService)
        return svc

    @pytest.fixture
    def links_svc(self, pyramid_config):
        svc = mock.Mock()
        pyramid_config.register_service(svc, name='links')
        return svc
