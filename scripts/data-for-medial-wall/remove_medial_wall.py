import pyvista as pv
import pickle as pkl
import numpy as np
from sklearn.neighbors import KDTree
from vtkmodules.vtkCommonDataModel import vtkIterativeClosestPointTransform
import os

# scale a mesh around its center of mass (in-place)
def scaleAmesh(mesh, scale):
    points = mesh.points - mesh.center_of_mass()
    points = scale*points
    points = points + mesh.center_of_mass()
    mesh.points = points
    return mesh

def alignCenters(target, source):
    points = source.points - source.center_of_mass()
    points = points + target.center_of_mass()
    source.points = points
    return source

def _alignMeshes(target, source, rigid=True):
    icp = vtkIterativeClosestPointTransform()
    icp.SetSource(source)
    icp.SetTarget(target)
    if rigid:
        icp.GetLandmarkTransform().SetModeToRigidBody()
    else:
        icp.GetLandmarkTransform().SetModeToSimilarity() 
    icp.SetMaximumNumberOfLandmarks(500)
    icp.SetMaximumMeanDistance(.00001)
    icp.SetMaximumNumberOfIterations(1000)
    icp.CheckMeanDistanceOn()
    icp.StartByMatchingCentroidsOn()
    icp.Update()

    return source.transform(icp.GetMatrix())

def alignMeshes(target, source, scale=True):
    aligned = alignCenters(target, source)
    if scale:
        aligned = _alignMeshes(target,
            _alignMeshes(target, aligned),
            rigid=False)
    else:
        aligned = _alignMeshes(target, aligned)
    return aligned

def withinBounds(points, bounds):
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    xx = (points[:,0] > xmin)
    yy = ((points[:,1] > ymin) & (points[:,1] < ymax))
    zz = ((points[:,2] > zmin) & (points[:,2] < zmax))
    passing = np.prod(np.c_[xx,yy,zz], axis=1).astype('bool')
    return points[passing, :], passing

def cleanDebris(mesh):
    connected_components = mesh.connectivity()
    mesh = connected_components.extract_largest()
    mesh.clear_data()
    return mesh

def minuspatch(meshA, patch, K=1):
    pmesh = pv.PolyData(patch)
    region = pmesh.delaunay_3d().extract_surface()
    scaleAmesh(region, 1.1)
    mp, passing = withinBounds(meshA.points, region.bounds)
    tree = KDTree(mp)
    nnidx = []
    for point in patch:
        distances, indices = tree.query(np.expand_dims(point,
            axis=0), K)
        nnidx.append({'idx': indices,
                      'dist': distances})
    nearest = np.array([x['idx'] for x in nnidx]).flatten()
    idxs = np.where(passing == True)[0][nearest]
    return cleanDebris(meshA.remove_points(idxs)[0])
