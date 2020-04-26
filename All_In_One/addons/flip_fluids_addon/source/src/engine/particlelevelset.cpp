/*
MIT License

Copyright (c) 2019 Ryan L. Guy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

#include "particlelevelset.h"

#include "levelsetutils.h"
#include "interpolation.h"
#include "polygonizer3d.h"
#include "gridutils.h"
#include "threadutils.h"
#include "markerparticle.h"
#include "grid3d.h"
#include "meshlevelset.h"
#include "scalarfield.h"

ParticleLevelSet::ParticleLevelSet() {
}

ParticleLevelSet::ParticleLevelSet(int i, int j, int k, double dx) : 
                    _isize(i), _jsize(j), _ksize(k), _dx(dx) {
    _phi = Array3d<float>(i, j, k, _getMaxDistance());
}

ParticleLevelSet::~ParticleLevelSet() {
}

float ParticleLevelSet::operator()(int i, int j, int k) {
    return get(i, j, k);
}

float ParticleLevelSet::operator()(GridIndex g) {
    return get(g);
}

float ParticleLevelSet::get(int i, int j, int k) {
    FLUIDSIM_ASSERT(Grid3d::isGridIndexInRange(i, j, k, _isize, _jsize, _ksize));
    return _phi(i, j, k);
}

float ParticleLevelSet::get(GridIndex g) {
    FLUIDSIM_ASSERT(Grid3d::isGridIndexInRange(g, _isize, _jsize, _ksize));
    return _phi(g);
}

float ParticleLevelSet::getFaceWeightU(int i, int j, int k) {
    FLUIDSIM_ASSERT(Grid3d::isGridIndexInRange(i, j, k, _isize + 1, _jsize, _ksize));
    return LevelsetUtils::fractionInside(_phi(i - 1, j, k), _phi(i, j, k));
}

float ParticleLevelSet::getFaceWeightU(GridIndex g) {
    return getFaceWeightU(g.i, g.j, g.k);
}

float ParticleLevelSet::getFaceWeightV(int i, int j, int k) {
    FLUIDSIM_ASSERT(Grid3d::isGridIndexInRange(i, j, k, _isize, _jsize + 1, _ksize));
    return LevelsetUtils::fractionInside(_phi(i, j - 1, k), _phi(i, j, k));
}

float ParticleLevelSet::getFaceWeightV(GridIndex g) {
    return getFaceWeightV(g.i, g.j, g.k);
}

float ParticleLevelSet::getFaceWeightW(int i, int j, int k) {
    FLUIDSIM_ASSERT(Grid3d::isGridIndexInRange(i, j, k, _isize, _jsize, _ksize + 1));
    return LevelsetUtils::fractionInside(_phi(i, j, k - 1), _phi(i, j, k));
}

float ParticleLevelSet::getFaceWeightW(GridIndex g) {
    return getFaceWeightW(g.i, g.j, g.k);
}

void ParticleLevelSet::getNodalPhi(Array3d<float> &nodalPhi) {
    FLUIDSIM_ASSERT(nodalPhi.width == _isize + 1 && 
                    nodalPhi.height == _jsize + 1 && 
                    nodalPhi.depth == _ksize + 1);

    for (int k = 0; k < _ksize + 1; k++) {
        for (int j = 0; j < _jsize + 1; j++) {
            for (int i = 0; i < _isize + 1; i++) {

                float sum = 0.0;
                if (Grid3d::isGridIndexInRange(i - 1, j - 1, k - 1, _isize, _jsize, _ksize)) {
                    sum += _phi(i - 1, j - 1, k - 1);
                }
                if (Grid3d::isGridIndexInRange(i, j - 1, k - 1, _isize, _jsize, _ksize)) {
                    sum += _phi(i, j - 1, k - 1);
                }
                if (Grid3d::isGridIndexInRange(i - 1, j, k - 1, _isize, _jsize, _ksize)) {
                    sum += _phi(i - 1, j, k - 1);
                }
                if (Grid3d::isGridIndexInRange(i, j, k - 1, _isize, _jsize, _ksize)) {
                    sum += _phi(i, j, k - 1);
                }
                if (Grid3d::isGridIndexInRange(i - 1, j - 1, k, _isize, _jsize, _ksize)) {
                    sum += _phi(i - 1, j - 1, k);
                }
                if (Grid3d::isGridIndexInRange(i, j - 1, k, _isize, _jsize, _ksize)) {
                    sum += _phi(i, j - 1, k);
                }
                if (Grid3d::isGridIndexInRange(i - 1, j, k, _isize, _jsize, _ksize)) {
                    sum += _phi(i - 1, j, k);
                }
                if (Grid3d::isGridIndexInRange(i, j, k, _isize, _jsize, _ksize)) {
                    sum += _phi(i, j, k);
                }

                nodalPhi.set(i, j, k, 0.125f * sum);
            }
        }
    }
}

float ParticleLevelSet::trilinearInterpolate(vmath::vec3 pos) {
    return Interpolation::trilinearInterpolate(pos - vmath::vec3(0.5*_dx, 0.5*_dx, 0.5*_dx), _dx, _phi);
}

float ParticleLevelSet::getDistanceAtNode(int i, int j, int k) {
    FLUIDSIM_ASSERT(Grid3d::isGridIndexInRange(i, j, k, _isize + 1, _jsize + 1, _ksize + 1));

    if (Grid3d::isGridIndexOnBorder(i, j, k, _isize + 1, _jsize + 1, _ksize + 1)) {
        return _getMaxDistance();
    }

    return 0.125f * (_phi(i - 1, j - 1, k - 1) + 
                     _phi(i    , j - 1, k - 1) + 
                     _phi(i - 1, j    , k - 1) + 
                     _phi(i    , j    , k - 1) +
                     _phi(i - 1, j - 1, k    ) + 
                     _phi(i    , j - 1, k    ) + 
                     _phi(i - 1, j    , k    ) + 
                     _phi(i    , j    , k    ));
}

float ParticleLevelSet::getDistanceAtNode(GridIndex g) {
    return getDistanceAtNode(g.i, g.j, g.k);
}

void ParticleLevelSet::calculateSignedDistanceField(FragmentedVector<MarkerParticle> &particles, 
                                                    double radius) {
    std::vector<vmath::vec3> points;
    points.reserve(particles.size());
    for (size_t i = 0; i < particles.size(); i++) {
        points.push_back(particles[i].position);
    }

    _computeSignedDistanceFromParticles(points, radius);
}

void ParticleLevelSet::extrapolateSignedDistanceIntoSolids(MeshLevelSet &solidPhi) {
    int si, sj, sk;
    solidPhi.getGridDimensions(&si, &sj, &sk);
    FLUIDSIM_ASSERT(si == _isize && sj == _jsize && sk == _ksize);

    for(int k = 0; k < _ksize; k++) {
        for(int j = 0; j < _jsize; j++) {
            for(int i = 0; i < _isize; i++) {
                if(_phi(i, j, k) < 0.5 * _dx) {
                    if(solidPhi.getDistanceAtCellCenter(i, j, k) < 0) {
                        _phi.set(i, j, k, -0.5f * _dx);
                    }
                }
            }
        }
    }
}

void ParticleLevelSet::calculateCurvatureGrid(MeshLevelSet &surfacePhi, 
                                              Array3d<float> &kgrid) {
    int si, sj, sk;
    surfacePhi.getGridDimensions(&si, &sj, &sk);
    FLUIDSIM_ASSERT(si == _isize && sj == _jsize && sk == _ksize);
    FLUIDSIM_ASSERT(kgrid.width == _isize + 1 && 
                    kgrid.height == _jsize + 1 && 
                    kgrid.depth == _ksize + 1);

    ScalarField field = ScalarField(_isize + 1, _jsize + 1, _ksize + 1, _dx);
    field.setSurfaceThreshold(0.0f);
    _initializeCurvatureGridScalarField(field);

    Polygonizer3d polygonizer(&field);
    TriangleMesh surfaceMesh = polygonizer.polygonizeSurface();
    surfaceMesh.smooth(_curvatureGridSmoothingValue, _curvatureGridSmoothingIterations);

    surfacePhi.disableVelocityData();
    surfacePhi.disableSignCalculation();
    surfacePhi.fastCalculateSignedDistanceField(surfaceMesh, _curvatureGridExactBand);

    // Signs are already computed and are stored on the scalar field. Note:
    // field signs are reversed, so values > 0 are inside.
    for (int k = 0; k < _ksize + 1; k++) {
        for (int j = 0; j < _jsize + 1; j++) {
            for (int i = 0; i < _isize + 1; i++) {
                if (field.getRawScalarFieldValue(i, j, k) > 0) {
                    surfacePhi.set(i, j, k, -surfacePhi(i, j, k));
                }
            }
        }
    }

    Array3d<bool> validCurvatureNodes(_isize + 1, _jsize + 1, _ksize + 1);
    _getValidCurvatureNodes(surfacePhi, validCurvatureNodes);
    kgrid.fill(0.0f);
    for (int k = 0; k < _ksize + 1; k++) {
        for (int j = 0; j < _jsize + 1; j++) {
            for (int i = 0; i < _isize + 1; i++) {
                if (validCurvatureNodes(i, j, k)) {
                    kgrid.set(i, j, k, surfacePhi.getCurvature(i, j, k));
                }
            }
        }
    }

    GridUtils::extrapolateGrid(&kgrid, &validCurvatureNodes, _curvatureGridExtrapolationLayers);
}

float ParticleLevelSet::_getMaxDistance() {
    return 3.0 * _dx;
}

void ParticleLevelSet::_computeSignedDistanceFromParticles(std::vector<vmath::vec3> &particles, 
                                                           double radius) {
    _phi.fill(_getMaxDistance());

    if (particles.empty()) {
        return;
    }

    BlockArray3d<float> blockphi;
    _initializeBlockGrid(particles, blockphi);

    ParticleGridCountData gridCountData;
    _computeGridCountData(particles, radius, blockphi, gridCountData);

    std::vector<vmath::vec3> sortedParticleData;
    std::vector<int> blockToParticleDataIndex;
    _sortParticlesIntoBlocks(particles, gridCountData, sortedParticleData, blockToParticleDataIndex);

    std::vector<GridBlock<float> > gridBlocks;
    blockphi.getActiveGridBlocks(gridBlocks);
    BoundedBuffer<ComputeBlock> computeBlockQueue(gridBlocks.size());
    BoundedBuffer<ComputeBlock> finishedComputeBlockQueue(gridBlocks.size());
    int numComputeBlocks = 0;
    for (size_t bidx = 0; bidx < gridBlocks.size(); bidx++) {
        GridBlock<float> b = gridBlocks[bidx];
        if (gridCountData.totalGridCount[b.id] == 0) {
            continue;
        }

        ComputeBlock computeBlock;
        computeBlock.gridBlock = b;
        computeBlock.particleData = &(sortedParticleData[blockToParticleDataIndex[b.id]]);
        computeBlock.numParticles = gridCountData.totalGridCount[b.id];
        computeBlock.radius = radius;
        computeBlockQueue.push(computeBlock);
        numComputeBlocks++;
    }

    int numCPU = ThreadUtils::getMaxThreadCount();
    int numthreads = (int)fmin(numCPU, computeBlockQueue.size());
    std::vector<std::thread> producerThreads(numthreads);
    for (int i = 0; i < numthreads; i++) {
        producerThreads[i] = std::thread(&ParticleLevelSet::_computeExactBandProducerThread, this,
                                         &computeBlockQueue, &finishedComputeBlockQueue);
    }

    int numComputeBlocksProcessed = 0;
    while (numComputeBlocksProcessed < numComputeBlocks) {
        std::vector<ComputeBlock> finishedBlocks;
        finishedComputeBlockQueue.popAll(finishedBlocks);
        for (size_t i = 0; i < finishedBlocks.size(); i++) {
            ComputeBlock block = finishedBlocks[i];
            GridIndex gridOffset(block.gridBlock.index.i * _blockwidth,
                                 block.gridBlock.index.j * _blockwidth,
                                 block.gridBlock.index.k * _blockwidth);

            int datasize = _blockwidth * _blockwidth * _blockwidth;
            for (int vidx = 0; vidx < datasize; vidx++) {
                GridIndex localidx = Grid3d::getUnflattenedIndex(vidx, _blockwidth, _blockwidth);
                GridIndex phiidx = GridIndex(localidx.i + gridOffset.i,
                                             localidx.j + gridOffset.j,
                                             localidx.k + gridOffset.k);
                if (_phi.isIndexInRange(phiidx)) {
                    _phi.set(phiidx, block.gridBlock.data[vidx]);
                }
            }
        }

        numComputeBlocksProcessed += finishedBlocks.size();
    }

    computeBlockQueue.notifyFinished();
    for (size_t i = 0; i < producerThreads.size(); i++) {
        producerThreads[i].join();
    }
}

void ParticleLevelSet::_initializeBlockGrid(std::vector<vmath::vec3> &particles,
                                            BlockArray3d<float> &blockphi) {
    BlockArray3dParameters params;
    params.isize = _isize;
    params.jsize = _jsize;
    params.ksize = _ksize;
    params.blockwidth = _blockwidth;
    Dims3d dims = BlockArray3d<float>::getBlockDimensions(params);

    Array3d<bool> activeBlocks(dims.i, dims.j, dims.k, false);

    int numCPU = ThreadUtils::getMaxThreadCount();
    int numthreads = (int)fmin(numCPU, particles.size());
    std::vector<std::thread> threads(numthreads);
    std::vector<int> intervals = ThreadUtils::splitRangeIntoIntervals(0, particles.size(), numthreads);
    for (int i = 0; i < numthreads; i++) {
        threads[i] = std::thread(&ParticleLevelSet::_initializeActiveBlocksThread, this,
                                 intervals[i], intervals[i + 1], 
                                 &particles, &activeBlocks);
    }

    for (int i = 0; i < numthreads; i++) {
        threads[i].join();
    }

    GridUtils::featherGrid26(&activeBlocks, numthreads);

    for (int k = 0; k < dims.k; k++) {
        for (int j = 0; j < dims.j; j++) {
            for (int i = 0; i < dims.i; i++) {
                if (activeBlocks(i, j, k)) {
                    params.activeblocks.push_back(GridIndex(i, j, k));
                }
            }
        }
    }

    blockphi = BlockArray3d<float>(params);
    blockphi.fill(_getMaxDistance());
}

void ParticleLevelSet::_initializeActiveBlocksThread(int startidx, int endidx, 
                                                     std::vector<vmath::vec3> *particles,
                                                     Array3d<bool> *activeBlocks) {
    float blockdx = _blockwidth * _dx;
    for (int i = startidx; i < endidx; i++) {
        vmath::vec3 p = particles->at(i);
        GridIndex g = Grid3d::positionToGridIndex(p, blockdx);
        if (activeBlocks->isIndexInRange(g)) {
            activeBlocks->set(g, true);
        }
    }
}

void ParticleLevelSet::_computeGridCountData(std::vector<vmath::vec3> &particles,
                                             double radius,
                                             BlockArray3d<float> &blockphi, 
                                             ParticleGridCountData &countdata) {

    _initializeGridCountData(particles, blockphi, countdata);

    int numthreads = countdata.numthreads;
    std::vector<std::thread> threads(numthreads);
    std::vector<int> intervals = ThreadUtils::splitRangeIntoIntervals(0, particles.size(), numthreads);
    for (int i = 0; i < numthreads; i++) {
        threads[i] = std::thread(&ParticleLevelSet::_computeGridCountDataThread, this,
                                 intervals[i], intervals[i + 1], 
                                 &particles,
                                 radius, 
                                 &blockphi, 
                                 &(countdata.threadGridCountData[i]));
    }

    for (int i = 0; i < numthreads; i++) {
        threads[i].join();
    }

    for (int tidx = 0; tidx < countdata.numthreads; tidx++) {
        std::vector<int> *threadGridCount = &(countdata.threadGridCountData[tidx].gridCount);
        for (size_t i = 0; i < countdata.totalGridCount.size(); i++) {
            countdata.totalGridCount[i] += threadGridCount->at(i);
        }
    }
}

void ParticleLevelSet::_initializeGridCountData(std::vector<vmath::vec3> &particles,
                                                BlockArray3d<float> &blockphi, 
                                                ParticleGridCountData &countdata) {
    int numCPU = ThreadUtils::getMaxThreadCount();
    int numthreads = (int)fmin(numCPU, particles.size());
    int numblocks = blockphi.getNumActiveGridBlocks();
    countdata.numthreads = numthreads;
    countdata.gridsize = numblocks;
    countdata.threadGridCountData = std::vector<GridCountData>(numthreads);
    for (int i = 0; i < numthreads; i++) {
        countdata.threadGridCountData[i].gridCount = std::vector<int>(numblocks, 0);
    }
    countdata.totalGridCount = std::vector<int>(numblocks, 0);
}

void ParticleLevelSet::_computeGridCountDataThread(int startidx, int endidx, 
                                                   std::vector<vmath::vec3> *particles,
                                                   double radius,
                                                   BlockArray3d<float> *blockphi, 
                                                   GridCountData *countdata) {
    
    countdata->simpleGridIndices = std::vector<int>(endidx - startidx, -1);
    countdata->invalidPoints = std::vector<bool>(endidx - startidx, false);
    countdata->startidx = startidx;
    countdata->endidx = endidx;

    float sr = _searchRadiusFactor * (float)radius;
    float blockdx = _blockwidth * _dx;
    for (int i = startidx; i < endidx; i++) {
        vmath::vec3 p = particles->at(i);
        GridIndex blockIndex = Grid3d::positionToGridIndex(p, blockdx);
        vmath::vec3 blockPosition = Grid3d::GridIndexToPosition(blockIndex, blockdx);

        if (p.x - sr > blockPosition.x && 
                p.y - sr > blockPosition.y && 
                p.z - sr > blockPosition.z && 
                p.x + sr < blockPosition.x + blockdx && 
                p.y + sr < blockPosition.y + blockdx && 
                p.z + sr < blockPosition.z + blockdx) {
            int blockid = blockphi->getBlockID(blockIndex);
            countdata->simpleGridIndices[i - startidx] = blockid;

            if (blockid != -1) {
                countdata->gridCount[blockid]++;
            } else {
                countdata->invalidPoints[i - startidx] = true;
            }
        } else {
            GridIndex gmin = Grid3d::positionToGridIndex(p.x - sr, p.y - sr, p.z - sr, blockdx);
            GridIndex gmax = Grid3d::positionToGridIndex(p.x + sr, p.y + sr, p.z + sr, blockdx);

            int overlapCount = 0;
            for (int gk = gmin.k; gk <= gmax.k; gk++) {
                for (int gj = gmin.j; gj <= gmax.j; gj++) {
                    for (int gi = gmin.i; gi <= gmax.i; gi++) {
                        int blockid = blockphi->getBlockID(gi, gj, gk);
                        if (blockid != -1) {
                            countdata->gridCount[blockid]++;
                            countdata->overlappingGridIndices.push_back(blockid);
                            overlapCount++;
                        }
                    }
                }
            }

            if (overlapCount == 0) {
                countdata->invalidPoints[i - startidx] = true;
            }
            countdata->simpleGridIndices[i - startidx] = -overlapCount;
        }
    }
}

void ParticleLevelSet::_sortParticlesIntoBlocks(std::vector<vmath::vec3> &particles,
                                                ParticleGridCountData &countdata, 
                                                std::vector<vmath::vec3> &sortedParticleData, 
                                                std::vector<int> &blockToParticleIndex) {

    blockToParticleIndex = std::vector<int>(countdata.gridsize, 0);
    int currentIndex = 0;
    for (size_t i = 0; i < blockToParticleIndex.size(); i++) {
        blockToParticleIndex[i] = currentIndex;
        currentIndex += countdata.totalGridCount[i];
    }
    std::vector<int> blockToParticleIndexCurrent = blockToParticleIndex;
    int totalParticleCount = currentIndex;

    sortedParticleData = std::vector<vmath::vec3>(totalParticleCount);
    for (int tidx = 0; tidx < countdata.numthreads; tidx++) {
        GridCountData *countData = &(countdata.threadGridCountData[tidx]);

        int indexOffset = countData->startidx;
        int currentOverlappingIndex = 0;
        for (size_t i = 0; i < countData->simpleGridIndices.size(); i++) {
            if (countData->invalidPoints[i]) {
                continue;
            }

            vmath::vec3 p = particles[i + indexOffset];
            if (countData->simpleGridIndices[i] >= 0) {
                int blockid = countData->simpleGridIndices[i];
                int sortedIndex = blockToParticleIndexCurrent[blockid];
                sortedParticleData[sortedIndex] = p;
                blockToParticleIndexCurrent[blockid]++;
            } else {
                int numblocks = -(countData->simpleGridIndices[i]);
                for (int blockidx = 0; blockidx < numblocks; blockidx++) {
                    int blockid = countData->overlappingGridIndices[currentOverlappingIndex];
                    currentOverlappingIndex++;

                    int sortedIndex = blockToParticleIndexCurrent[blockid];
                    sortedParticleData[sortedIndex] = p;
                    blockToParticleIndexCurrent[blockid]++;
                }
            }
        }
    }

}

void ParticleLevelSet::_computeExactBandProducerThread(BoundedBuffer<ComputeBlock> *computeBlockQueue,
                                                       BoundedBuffer<ComputeBlock> *finishedComputeBlockQueue) {
    while (computeBlockQueue->size() > 0) {
        std::vector<ComputeBlock> computeBlocks;
        int numBlocks = computeBlockQueue->pop(_numComputeBlocksPerJob, computeBlocks);
        if (numBlocks == 0) {
            continue;
        }

        for (size_t bidx = 0; bidx < computeBlocks.size(); bidx++) {
            ComputeBlock block = computeBlocks[bidx];
            float r = block.radius;
            float sr = _searchRadiusFactor * r;
            GridIndex blockIndex = block.gridBlock.index;
            vmath::vec3 blockPositionOffset = Grid3d::GridIndexToPosition(blockIndex, _blockwidth * _dx);

            for (int pidx = 0; pidx < block.numParticles; pidx++) {
                vmath::vec3 p = block.particleData[pidx];
                p -= blockPositionOffset;

                vmath::vec3 pmin(p.x - sr, p.y - sr, p.z - sr);
                vmath::vec3 pmax(p.x + sr, p.y + sr, p.z + sr);
                GridIndex gmin = Grid3d::positionToGridIndex(pmin, _dx);
                GridIndex gmax = Grid3d::positionToGridIndex(pmax, _dx);
                gmin.i = std::max(gmin.i, 0);
                gmin.j = std::max(gmin.j, 0);
                gmin.k = std::max(gmin.k, 0);
                gmax.i = std::min(gmax.i, _blockwidth - 1);
                gmax.j = std::min(gmax.j, _blockwidth - 1);
                gmax.k = std::min(gmax.k, _blockwidth - 1);

                for (int k = gmin.k; k <= gmax.k; k++) {
                    for (int j = gmin.j; j <= gmax.j; j++) {
                        for (int i = gmin.i; i <= gmax.i; i++) {
                            vmath::vec3 gpos = Grid3d::GridIndexToCellCenter(i, j, k, _dx);
                            float dist = vmath::length(gpos - p) - r;
                            int flatidx = Grid3d::getFlatIndex(i, j, k, _blockwidth, _blockwidth);
                            if (dist < block.gridBlock.data[flatidx]) {
                                 block.gridBlock.data[flatidx] = dist;
                            }
                        }
                    }
                }
            }

            finishedComputeBlockQueue->push(block);
        }
    }
}

void ParticleLevelSet::_initializeCurvatureGridScalarField(ScalarField &field) {
    int gridsize = (_isize + 1) * (_jsize + 1) * (_ksize + 1);
    int numCPU = ThreadUtils::getMaxThreadCount();
    int numthreads = (int)fmin(numCPU, gridsize);
    std::vector<std::thread> threads(numthreads);
    std::vector<int> intervals = ThreadUtils::splitRangeIntoIntervals(0, gridsize, numthreads);
    for (int i = 0; i < numthreads; i++) {
        threads[i] = std::thread(&ParticleLevelSet::_initializeCurvatureGridScalarFieldThread, this,
                                 intervals[i], intervals[i + 1], &field);
    }

    for (int i = 0; i < numthreads; i++) {
        threads[i].join();
    }
}

void ParticleLevelSet::_initializeCurvatureGridScalarFieldThread(int startidx, int endidx, 
                                                                 ScalarField *field) {
    for (int idx = startidx; idx < endidx; idx++) {
        GridIndex g = Grid3d::getUnflattenedIndex(idx, _isize + 1, _jsize + 1);
        field->setScalarFieldValue(g, -getDistanceAtNode(g));
    }
}

void ParticleLevelSet::_getValidCurvatureNodes(MeshLevelSet &surfacePhi, 
                                               Array3d<bool> &validNodes) {

    float distUpperBound = surfacePhi.getDistanceUpperBound();
    Array3d<bool> tempValid(_isize + 1, _jsize + 1, _ksize + 1, false);

    Array3d<float> *phi = surfacePhi.getPhiArray3d();
    float *rawphi = phi->getRawArray();
    int size = phi->getNumElements();
    for (int i = 0; i < size; i++) {
        if (rawphi[i] < distUpperBound) {
            tempValid.set(i, true);
        }
    }

    validNodes.fill(false);
    for (int k = 1; k < _ksize; k++) {
        for (int j = 1; j < _jsize; j++) {
            for (int i = 1; i < _isize; i++) {
                if (!tempValid(i, j, k)) {
                    continue;
                }

                bool isValid = tempValid(i + 1, j, k) &&
                               tempValid(i - 1, j, k) &&
                               tempValid(i, j + 1, k) &&
                               tempValid(i, j - 1, k) &&
                               tempValid(i, j, k + 1) &&
                               tempValid(i, j, k - 1);
                if (isValid) {
                    validNodes.set(i, j, k, true);
                }
            }
        }
    }
}
