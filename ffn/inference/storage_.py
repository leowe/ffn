# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Storage-related FFN utilities."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from collections import namedtuple
from contextlib import contextmanager
import logging
import json
import os
import re
import tempfile

import h5py
import numpy as np

from tensorflow import gfile
from . import align
from . import segmentation
from . import storage
from ..utils import bounding_box

OriginInfo = namedtuple('OriginInfo', ['start_zyx', 'iters', 'walltime_sec'])


def load_segmentation_(segmentation_dir, corner, allow_cpoint=False,
                      threshold=None, split_cc=True, min_size=0,
                      mask_config=None):
  """Loads segmentation from an FFN subvolume.

  Args:
    segmentation_dir: directory containing FFN subvolumes
    corner: lower corner of the FFN subvolume as a (z, y, x) tuple
    allow_cpoint: whether to return incomplete segmentation from a checkpoint
        when a final segmentation is not available
    threshold: optional probability threshold at which to generate the
        segmentation; in order for this to work, the probability file must
        be present, and the segmentation in the main FFN subvolume file must
        have been generated at a threshold lower than the one requested now
    split_cc: whether to recompute connected components within the subvolume
    min_size: minimum (post-CC, if enabled) segment size in voxels; if 0,
        no size filtering is done
    mask_config: optional MaskConfigs proto specifying the mask to apply
        to the loaded subvolume

  Returns:
    tuple of:
      3d uint64 numpy array with segmentation labels,
      dictionary mapping segment IDs to information about their origins.
      This is currently a tuple of (seed location in x, y, z;
      number of FFN iterations used to produce the segment;
      wall clock time in seconds used for inference).

  Raises:
    ValueError: when requested segmentation cannot be found
  """
  target_path = get_existing_subvolume_path(segmentation_dir, corner,
                                            allow_cpoint)
  if target_path is None:
    raise ValueError('Segmentation not found, %s, %r.' %
                     (segmentation_dir, corner))

  with gfile.Open(target_path, 'rb') as f:
    data = np.load(f)
    if 'segmentation' in data:
      seg = data['segmentation']
    else:
      raise ValueError('FFN NPZ file %s does not contain valid segmentation.' %
                       target_path)

    output = seg.astype(np.uint64)

    logging.info('loading segmentation from: %s', target_path)

    if threshold is not None:
      logging.info('thresholding at %f', threshold)
      threshold_segmentation(segmentation_dir, corner, output, threshold)

    if mask_config is not None:
      mask = build_mask(mask_config.masks, corner, seg.shape)
      output[mask] = 0

    if split_cc or min_size:
      logging.info('clean up with split_cc=%r, min_size=%d', split_cc,
                   min_size)
      new_to_old = segmentation.clean_up(output, split_cc,
                                         min_size,
                                         return_id_map=True)


  return output, True
  