import unittest

from app.common import objects


class LayersTests(unittest.TestCase):

    @staticmethod
    def test_child_elimination_from_layer_list():
        layers = objects.Layers()
        names = 'addresses_to_import,buildings_to_import,addresses,buildings'
        filtered_layers = layers.selected_layers(names)
        filtered_names = ','.join(list(sorted([x.id for x in filtered_layers])))
        assert filtered_names == 'addresses,buildings'

    @staticmethod
    def test_if_at_least_one_active_layer():
        layers = objects.Layers()
        active_layers = layers.active
        assert len(active_layers) > 0

    @staticmethod
    def test_if_layer_selection_is_case_insensitive():
        layers = objects.Layers()
        layer_id = 'AddresseS'
        selected_layers = layers.selected_layers(layer_id)
        assert len(selected_layers) == 1
        assert selected_layers[0].id == layer_id.lower()

    @staticmethod
    def test_if_layers_class_is_subscriptable():
        layers = objects.Layers()
        layer_id = 'addresses'
        assert layers[layer_id] is not None
        assert layers[layer_id].id == layer_id


if __name__ == "__main__":
    unittest.main()
