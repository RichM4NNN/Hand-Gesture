import tensorflow as tf
from tensorflow.keras.layers import DepthwiseConv2D
from tensorflow.keras.utils import get_custom_objects

class FixedDepthwiseConv2D(DepthwiseConv2D):
    def __init__(self, *args, **kwargs):
        if 'groups' in kwargs:
            del kwargs['groups']
        super(FixedDepthwiseConv2D, self).__init__(*args, **kwargs)

get_custom_objects().update({'DepthwiseConv2D': FixedDepthwiseConv2D})
