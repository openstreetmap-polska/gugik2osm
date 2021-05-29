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


if __name__ == "__main__":
    unittest.main()
