import pytest

from unittest.mock import patch


@pytest.mark.django_db
class TestViewFirstaidTip():
    url = '/api/v1/firstaid/tip'

    def test_view_tip(self, client, first_aid_fume_tip):
        tip_id = first_aid_fume_tip.id
        response = client.get(self.url + f'/{tip_id}')
        assert response.status_code == 200
        assert response.data['message'] == 'Successfully retrieved First aid tip'

    def test_nonexistent_tip(self, client):
        tip_id = 'wrong'
        response = client.get(self.url + f'/{tip_id}')
        assert response.status_code == 404
        assert response.data['message'] == 'First aid tip not found'

    def test_increase_tip_view_count(self, client, first_aid_fume_tip):
        tip_id = first_aid_fume_tip.id
        response = client.patch(self.url + f'/{tip_id}')

        assert response.status_code == 200
        first_aid_fume_tip.refresh_from_db()
        assert first_aid_fume_tip.views == 1

    def test_view_all_tips(self, client, first_aid_fume_tip,
                           first_aid_hypnoxia_tip):
        response = client.get(self.url)
        assert response.status_code == 200
        assert len(response.data['data']) == 2

    def test_search_tip(self, client, first_aid_fume_tip,
                        first_aid_hypnoxia_tip):
        response = client.get(self.url + '?query=headache fume')
        assert response.status_code == 200
        assert len(response.data['data']) > 0
