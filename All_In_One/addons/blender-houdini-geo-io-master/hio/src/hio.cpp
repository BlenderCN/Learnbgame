#include "hio.h"

#include <numeric>
#include <iostream>
#include <fstream>

namespace hio {

	Geometry::Geometry()
	{
		_geo.clearAndDestroy();
	}

	void Geometry::clear()
	{
		_geo.clearAndDestroy();
	}

	hio::Size Geometry::getNumPoints() const
	{
		return _geo.getNumPoints();
	}

	hio::Size Geometry::getNumVertices() const
	{
		return _geo.getNumVertices();
	}

	hio::Size Geometry::getNumPrimitives() const
	{
		return _geo.getNumPrimitives();
	}

	hio::Point Geometry::createPoint()
	{
		return Point(_geo.appendPoint());
	}

	std::vector<hio::Point> Geometry::createPoints(Size size)
	{
		auto start = _geo.appendPointBlock(size);

		std::vector<hio::Point> arr;
		for (int i = 0; i < size; i++)
			arr.emplace_back(start + i);
		return arr;
	}

	std::vector<Point> Geometry::createPoints(Size size, const Vector3* data)
	{
		auto start = _geo.appendPointBlock(size);

		auto P = _geo.getP();
		auto tuple = P->getAIFTuple();
		auto res = tuple->setRange(P, _geo.getPointRange(), (float*)data, 0, 3);
		assert(res);

		std::vector<hio::Point> arr;
		for (int i = 0; i < size; i++)
			arr.emplace_back(start + i);
		return arr;
	}

	hio::Point Geometry::point(Index index) const
	{
		assert(index >= 0 && index < getNumPoints());
		return hio::Point(index);
	}

	std::vector<hio::Point> Geometry::points() const
	{
		std::vector<hio::Point> pts;
		for (int i = 0; i < getNumPoints(); i++)
			pts.emplace_back(i);
		return pts;
	}

	hio::Primitive Geometry::prim(Index index) const
	{
		assert(index >= 0 && index < getNumPrimitives());
		return Primitive((GEO_Primitive*)_geo.getPrimitiveByIndex(index));
	}

	std::vector<hio::Primitive> Geometry::prims() const
	{
		std::vector<hio::Primitive> arr;

		for (int i = 0; i < _geo.getNumPrimitives(); i++)
		{
			auto prim = _geo.getPrimitiveByIndex(i);
			arr.emplace_back((GEO_Primitive*)prim);
		}

		return arr;
	}

	hio::Polygon Geometry::createPolygon(Size num_vertices, bool is_closed)
	{
		GEO_PrimPoly* poly = (GEO_PrimPoly*)GU_PrimPoly::build(&_geo, num_vertices, !is_closed, true);
		return Polygon(poly);
	}


	std::vector<hio::Polygon> Geometry::createPolygons(Size position_size, const Vector3* positions, Size vertex_counts_size, const Size* vertex_counts, bool closed)
	{
		if (std::accumulate(vertex_counts, vertex_counts + vertex_counts_size, 0) != position_size)
			throw std::runtime_error("Position and vertex count mismatch");

		auto pts = createPoints(position_size, positions);

		auto pt_it = pts.begin();

		std::vector<hio::Polygon> arr;
		arr.reserve(vertex_counts_size);

		for (int x = 0; x < vertex_counts_size; x++)
		{
			auto count = vertex_counts[x];

			auto poly = createPolygon();
			poly.setIsClosed(closed);
			arr.push_back(poly);

			for (int i = 0; i < count; i++)
			{
				poly.addVertex(*pt_it);
				pt_it++;
			}
		}

		return arr;
	}

	std::vector<hio::Polygon> Geometry::createPolygons(Size position_size, const Vector3* positions, Size vertices_size, const Index* vertices, Size vertex_counts_size, const Size* vertex_counts, bool closed)
	{
		auto pts = createPoints(position_size, positions);

		auto vtx_it = vertices;

		std::vector<hio::Polygon> arr;
		arr.reserve(vertex_counts_size);

		for (int x = 0; x < vertex_counts_size; x++)
		{
			auto count = vertex_counts[x];

			auto poly = createPolygon();
			poly.setIsClosed(closed);
			arr.push_back(poly);

			for (int i = 0; i < count; i++)
			{
				auto pt = pts[*vtx_it];
				poly.addVertex(pt);
				vtx_it++;
			}
		}

		return arr;

	}
	
	hio::BezierCurve Geometry::createBezierCurve(Size num_vertices, bool is_closed, int order)
	{
		GEO_PrimRBezCurve* curve = GU_PrimRBezCurve::build(&_geo, num_vertices, order, is_closed, true);
		return BezierCurve(curve);
	}

	hio::NURBSCurve Geometry::createNURBSCurve(Size num_vertices, bool is_closed, int order, int _interp_ends)
	{
		int interpEnds = is_closed ? 0 : 1;
		if (_interp_ends >= 0)
			interpEnds = _interp_ends;

		GEO_PrimNURBCurve* curve = GU_PrimNURBCurve::build(&_geo, num_vertices, order, is_closed, interpEnds, true);
		return NURBSCurve(curve);
	}

	void Geometry::deletePrims(const std::vector<Primitive>& prims, bool keep_points)
	{
		GA_PrimitiveGroup *grp = geo().newInternalPrimitiveGroup();

		for (auto prim : prims)
			grp->addIndex(prim.number());

		geo().deletePrimitives(*grp, !keep_points);
		geo().destroyPrimitiveGroup(grp);
	}

	std::vector<Attrib> Geometry::pointAttribs() const
	{
		auto attrs = _geo.pointAttribs();
		
		std::vector<Attrib> arr;

		GA_AttributeDict::iterator it = attrs.begin(GA_SCOPE_PUBLIC);
		while (it != attrs.end())
		{
			arr.push_back(*it);
			it.operator++();
		}

		return arr;
	}

	std::vector<Attrib> Geometry::primAttribs() const
	{
		auto attrs = _geo.primitiveAttribs();

		std::vector<Attrib> arr;
		GA_AttributeDict::iterator it = attrs.begin(GA_SCOPE_PUBLIC);
		while (it != attrs.end())
		{
			arr.push_back(*it);
			it.operator++();
		}

		return arr;
	}

	std::vector<Attrib> Geometry::vertexAttribs() const
	{
		auto attrs = _geo.vertexAttribs();

		std::vector<Attrib> arr;
		GA_AttributeDict::iterator it = attrs.begin(GA_SCOPE_PUBLIC);
		while (it != attrs.end())
		{
			arr.push_back(*it);
			it.operator++();
		}

		return arr;
	}

	std::vector<Attrib> Geometry::globalAttribs() const
	{
		auto attrs = _geo.attribs();

		std::vector<Attrib> arr;
		GA_AttributeDict::iterator it = attrs.begin(GA_SCOPE_PUBLIC);
		while (it != attrs.end())
		{
			arr.push_back(*it);
			it.operator++();
		}

		return arr;
	}

	hio::Attrib Geometry::findPointAttrib(const std::string& name) const
	{
		return _geo.findPointAttribute(GA_SCOPE_PUBLIC, UT_StringRef(name.c_str()));
	}

	hio::Attrib Geometry::findPrimAttrib(const std::string& name) const
	{
		return _geo.findPrimitiveAttribute(GA_SCOPE_PUBLIC, UT_StringRef(name.c_str()));
	}

	hio::Attrib Geometry::findVertexAttrib(const std::string& name) const
	{
		return _geo.findVertexAttribute(GA_SCOPE_PUBLIC, UT_StringRef(name.c_str()));
	}

	hio::Attrib Geometry::findGlobalAttrib(const std::string& name) const
	{
		return _geo.findGlobalAttribute(GA_SCOPE_PUBLIC, UT_StringRef(name.c_str()));
	}
	
	///

	bool Geometry::load(const std::string& path)
	{
		GA_LoadOptions opts;
		UT_StringArray errors;

		std::string _path = path;
		std::replace(_path.begin(), _path.end(), '\\', '/');

		auto res = _geo.load(_path.c_str(), &opts, &errors);
		if (!res.success())
		{
			for (auto s : errors)
				std::cerr << s << std::endl;
			return false;
		}

		return true;

		//try
		//{
		//	clear();

		//	GU_Detail in_geo;

		//	GA_LoadOptions opts;
		//	UT_StringArray errors;
		//	opts.setReadOnly(true);

		//	std::string _path = path;
		//	std::replace(_path.begin(), _path.end(), '\\', '/');

		//	auto res = in_geo.load(_path.c_str(), &opts, &errors);
		//	if (!res.success())
		//	{
		//		for (auto s : errors)
		//			std::cerr << s << std::endl;
		//		return false;
		//	}

		//	GEO_Detail* gdp = &in_geo;

		//	const size_t point_count = gdp->getNumPoints();
		//	const size_t vertex_count = gdp->getNumVertices();
		//	const size_t prim_count = gdp->getNumPrimitives();

		//	points.reserve(point_count);
		//	vertices.reserve(vertex_count);
		//	primitives.reserve(prim_count);

		//	{
		//		const GA_AttributeDict& attributes = gdp->pointAttribs();
		//		GA_AttributeDict::iterator it = attributes.begin(GA_SCOPE_PUBLIC);

		//		const Size count = point_count;
		//		auto& out_attributes = point_attributes;
		//		auto range = gdp->getPointRange();

		//		while (it != attributes.end())
		//		{
		//			GA_Attribute* A = *it;

		//			if (A)
		//			{
		//				auto storage_class = A->getStorageClass();
		//				auto typeinfo = to_enum(A->getTypeInfo());

		//				if (storage_class == GA_STORECLASS_REAL)
		//				{
		//					const GA_AIFTuple* tuple = A->getAIFTuple();
		//					int tuple_size = tuple->getTupleSize(A);
		//					auto storage = tuple->getStorage(A);

		//					// Only supported float32 storage
		//					assert(storage == GA_STORE_REAL32);

		//					if (it.name() == std::string("P"))
		//					{
		//						assert(tuple_size == 3);

		//						std::vector<Vector3> data(count);
		//						tuple->getRange(A, range, (float*)&data[0], 0, tuple_size);

		//						for (const auto& p : data)
		//							createPoint(p.x, p.y, p.z);
		//					}
		//					else
		//					{
		//						std::shared_ptr<Attribute_<float>> attr = std::make_shared<Attribute_<float>>(tuple_size, it.name(), typeinfo);
		//						attr->resize(count);

		//						tuple->getRange(A, range, &attr->_data[0], 0, tuple_size);

		//						out_attributes.push_back(attr);
		//					}
		//				}
		//				else if (storage_class == GA_STORECLASS_STRING)
		//				{
		//					const GA_AIFStringTuple* tuple = A->getAIFStringTuple();
		//					int tuple_size = tuple->getTupleSize(A);

		//					std::shared_ptr<Attribute_<std::string>> attr = std::make_shared<Attribute_<std::string>>(tuple_size, it.name(), typeinfo);

		//					UT_StringArray arr;
		//					for (int i = 0; i < count; i++)
		//					{
		//						tuple->getStrings(A, GA_Offset(i), arr, tuple_size);
		//						attr->append(arr.begin(), arr.end());
		//					}

		//					out_attributes.push_back(attr);
		//				}
		//			}

		//			it.operator++();
		//		}
		//	}

		//	{
		//		const GA_AttributeDict& attributes = gdp->vertexAttribs();
		//		GA_AttributeDict::iterator it = attributes.begin(GA_SCOPE_PUBLIC);

		//		const Size count = vertex_count;
		//		auto& out_attributes = vertex_attributes;
		//		auto range = gdp->getVertexRange();

		//		while (it != attributes.end())
		//		{
		//			GA_Attribute* A = *it;

		//			if (A)
		//			{
		//				auto storage_class = A->getStorageClass();
		//				auto typeinfo = to_enum(A->getTypeInfo());

		//				if (storage_class == GA_STORECLASS_REAL)
		//				{
		//					const GA_AIFTuple* tuple = A->getAIFTuple();
		//					int tuple_size = tuple->getTupleSize(A);
		//					auto storage = tuple->getStorage(A);

		//					// Only supported float32 storage
		//					assert(storage == GA_STORE_REAL32);

		//					std::shared_ptr<Attribute_<float>> attr = std::make_shared<Attribute_<float>>(tuple_size, it.name(), typeinfo);

		//					attr->resize(count);

		//					tuple->getRange(A, range, &attr->_data[0], 0, tuple_size);

		//					out_attributes.push_back(attr);
		//				}
		//				else if (storage_class == GA_STORECLASS_STRING)
		//				{
		//					const GA_AIFStringTuple* tuple = A->getAIFStringTuple();
		//					int tuple_size = tuple->getTupleSize(A);

		//					std::shared_ptr<Attribute_<std::string>> attr = std::make_shared<Attribute_<std::string>>(tuple_size, it.name(), typeinfo);

		//					UT_StringArray arr;
		//					for (int i = 0; i < count; i++)
		//					{
		//						tuple->getStrings(A, GA_Offset(i), arr, tuple_size);
		//						attr->append(arr.begin(), arr.end());
		//					}

		//					out_attributes.push_back(attr);
		//				}
		//			}

		//			it.operator++();
		//		}
		//	}

		//	{
		//		const GA_AttributeDict& attributes = gdp->primitiveAttribs();
		//		GA_AttributeDict::iterator it = attributes.begin(GA_SCOPE_PUBLIC);

		//		const Size count = prim_count;
		//		auto& out_attributes = primitive_attributes;
		//		auto range = gdp->getPrimitiveRange();

		//		while (it != attributes.end())
		//		{
		//			GA_Attribute* A = *it;

		//			if (A)
		//			{
		//				auto storage_class = A->getStorageClass();
		//				auto typeinfo = to_enum(A->getTypeInfo());

		//				if (storage_class == GA_STORECLASS_REAL)
		//				{
		//					const GA_AIFTuple* tuple = A->getAIFTuple();
		//					int tuple_size = tuple->getTupleSize(A);
		//					auto storage = tuple->getStorage(A);

		//					// Only supported float32 storage
		//					assert(storage == GA_STORE_REAL32);

		//					std::shared_ptr<Attribute_<float>> attr = std::make_shared<Attribute_<float>>(tuple_size, it.name(), typeinfo);

		//					attr->resize(count);

		//					tuple->getRange(A, range, &attr->_data[0], 0, tuple_size);

		//					out_attributes.push_back(attr);
		//				}
		//				else if (storage_class == GA_STORECLASS_STRING)
		//				{
		//					const GA_AIFStringTuple* tuple = A->getAIFStringTuple();
		//					int tuple_size = tuple->getTupleSize(A);

		//					std::shared_ptr<Attribute_<std::string>> attr = std::make_shared<Attribute_<std::string>>(tuple_size, it.name(), typeinfo);

		//					UT_StringArray arr;
		//					for (int i = 0; i < count; i++)
		//					{
		//						tuple->getStrings(A, GA_Offset(i), arr, tuple_size);
		//						attr->append(arr.begin(), arr.end());
		//					}

		//					out_attributes.push_back(attr);
		//				}
		//			}

		//			it.operator++();
		//		}
		//	}

		//	{
		//		const GA_AttributeDict& attributes = gdp->attribs();
		//		GA_AttributeDict::iterator it = attributes.begin(GA_SCOPE_PUBLIC);

		//		const Size count = 1;
		//		auto& out_attributes = detail_attributes;
		//		auto range = gdp->getGlobalRange();

		//		while (it != attributes.end())
		//		{
		//			GA_Attribute* A = *it;

		//			if (A)
		//			{
		//				auto storage_class = A->getStorageClass();
		//				auto typeinfo = to_enum(A->getTypeInfo());

		//				if (storage_class == GA_STORECLASS_REAL)
		//				{
		//					const GA_AIFTuple* tuple = A->getAIFTuple();
		//					int tuple_size = tuple->getTupleSize(A);
		//					auto storage = tuple->getStorage(A);

		//					// Only supported float32 storage
		//					assert(storage == GA_STORE_REAL32);

		//					std::shared_ptr<Attribute_<float>> attr = std::make_shared<Attribute_<float>>(tuple_size, it.name(), typeinfo);

		//					attr->resize(count);

		//					tuple->getRange(A, range, &attr->_data[0], 0, tuple_size);

		//					out_attributes.push_back(attr);
		//				}
		//				else if (storage_class == GA_STORECLASS_STRING)
		//				{
		//					const GA_AIFStringTuple* tuple = A->getAIFStringTuple();
		//					int tuple_size = tuple->getTupleSize(A);

		//					std::shared_ptr<Attribute_<std::string>> attr = std::make_shared<Attribute_<std::string>>(tuple_size, it.name(), typeinfo);

		//					UT_StringArray arr;
		//					for (int i = 0; i < count; i++)
		//					{
		//						tuple->getStrings(A, GA_Offset(i), arr, tuple_size);
		//						attr->append(arr.begin(), arr.end());
		//					}

		//					out_attributes.push_back(attr);
		//				}
		//			}

		//			it.operator++();
		//		}
		//	}

		//	if (gdp->getNumPrimitives() > 0)
		//	{
		//		Index prim_id = 0;
		//		const GEO_Primitive* prim = nullptr;

		//		GA_FOR_ALL_PRIMITIVES(gdp, prim)
		//		{
		//			Primitive* p = nullptr;

		//			int vertex_start_index = prim->getVertexIndex(0);
		//			int vertex_count = prim->getVertexCount();

		//			std::vector<Index> idxs;
		//			idxs.reserve(vertex_count);

		//			for (int i = 0; i < vertex_count; i++)
		//			{
		//				auto idx = prim->getPointIndex(i);
		//				idxs.emplace_back(idx);
		//			}

		//			if (prim->getPrimitiveId() == GEO_PrimTypeCompat::GEOPRIMPOLY)
		//			{
		//				auto t = createPrimitive(PrimType::Polygon, idxs);
		//				p = t.second;

		//				auto pp = (GEO_PrimPoly*)prim;
		//				p->closed = pp->isClosed();
		//			}
		//			else if (prim->getPrimitiveId() == GEO_PrimTypeCompat::GEOPRIMNURBCURVE)
		//			{
		//				auto t = createPrimitive(PrimType::NURBS, idxs);
		//				p = t.second;

		//				auto pp = (GEO_PrimNURBCurve*)prim;
		//				p->closed = pp->isClosed();
		//				p->order = pp->getOrder();
		//			}
		//			else if (prim->getPrimitiveId() == GEO_PrimTypeCompat::GEOPRIMBEZCURVE)
		//			{
		//				auto t = createPrimitive(PrimType::Bezier, idxs);
		//				p = t.second;

		//				auto pp = (GEO_PrimRBezCurve*)prim;
		//				p->closed = pp->isClosed();
		//				p->order = pp->getOrder();
		//			}
		//			//else if (prim->getPrimitiveId() == GEO_PrimTypeCompat::GEOPRIMPART)
		//			//{
		//			//	p.type = PrimType::Particle;

		//			//	auto pp = (GEO_PrimParticle*)prim;
		//			//}
		//			//else
		//			//{
		//			//	//std::cout << "other" << std::endl;
		//			//}

		//			prim_id += 1;
		//		}
		//	}

		//	assert(point_count == points.size());
		//	assert(vertex_count == vertices.size());
		//	assert(prim_count == primitives.size());

		//	return true;
		//}
		//catch (std::exception e)
		//{
		//	std::cerr << e.what() << std::endl;
		//	return false;
		//}
	}

	bool Geometry::save(const std::string& path)
	{
		UT_StringArray errors;
		GA_SaveOptions opts;

		std::string _path = path;
		std::replace(_path.begin(), _path.end(), '\\', '/');

		auto res = _geo.save(_path.c_str(), &opts, &errors);
		if (!res.success())
		{
			for (auto s : errors)
				std::cerr << s << std::endl;
			return false;
		}

		return true;

	//	try
	//	{
	//		GU_Detail out_geo;
	//		GEO_Detail* gdp = &out_geo;

	//		gdp->clearAndDestroy();

	//		const size_t point_count = getNumPoints();
	//		const size_t vertex_count = getNumVertices();
	//		const size_t prim_count = getNumPrimitives();

	//		gdp->appendPointBlock(point_count);

	//		{
	//			GA_Attribute* attr = gdp->addFloatTuple(GA_ATTRIB_POINT, "P", 3);
	//			UT_ValArray<UT_Vector3T<float>> VA(point_count);

	//			memcpy(VA.array(), (const float*)&points[0], sizeof(float) * point_count * 3);
	//			gdp->setAttributeFromArray(attr, GA_Range(gdp->getPointMap(), GA_Offset(0), point_count), VA);
	//		}

	//		{
	//			for (auto prim : primitives)
	//			{
	//				if (prim.type == PrimType::Polygon)
	//				{
	//					auto vertex_start_index = prim.vertex_start_index;
	//					auto vertex_count = prim.vertex_count;

	//					GEO_PrimPoly* p = GEO_PrimPoly::build(&out_geo, vertex_count, false, false);
	//					assert(p);

	//					if (p)
	//					{
	//						for (int i = 0; i < vertex_count; i++)
	//						{
	//							Index idx = vertices[vertex_start_index + i];
	//							p->setVertexPoint(i, idx);
	//						}

	//						p->setClosed(prim.closed);
	//					}
	//				}
	//				else if (prim.type == PrimType::NURBS)
	//				{
	//					int interpEnds = 0;
	//					if (!prim.closed)
	//						interpEnds = 1;

	//					auto vertex_start_index = prim.vertex_start_index;
	//					auto vertex_count = prim.vertex_count;

	//					GEO_PrimNURBCurve* p = GU_PrimNURBCurve::build(&out_geo, vertex_count, prim.order, prim.closed, interpEnds, false);
	//					assert(p);

	//					if (p)
	//					{
	//						for (int i = 0; i < vertex_count; i++)
	//						{
	//							Index idx = vertices[vertex_start_index + i];
	//							p->setVertexPoint(i, idx);
	//						}

	//						for (int i = 0; i < vertex_count; i++)
	//						{
	//							auto p3 = p->getPos3(i);
	//							auto p4 = UT_Vector4(p3.x(), p3.y(), p3.z(), 0.5);
	//							p->evaluateBreakpoint(i, p4);
	//						}

	//						p->setClosed(prim.closed);
	//					}
	//				}
	//				else if (prim.type == PrimType::Bezier)
	//				{
	//					auto vertex_start_index = prim.vertex_start_index;
	//					auto vertex_count = prim.vertex_count;

	//					GEO_PrimRBezCurve* p = GU_PrimRBezCurve::build(&out_geo, vertex_count, prim.order, prim.closed, false);
	//					assert(p);

	//					if (p)
	//					{
	//						for (int i = 0; i < vertex_count; i++)
	//						{
	//							Index idx = this->vertices[vertex_start_index + i];
	//							p->setVertexPoint(i, idx);
	//						}

	//						p->setClosed(prim.closed);
	//					}
	//				}
	//				else if (prim.type == PrimType::Particle)
	//				{
	//					GEO_PrimParticle* p = (GEO_PrimParticle*)gdp->appendPrimitive(GEO_PRIMPART);

	//					auto vertex_start_index = prim.vertex_start_index;
	//					auto vertex_count = prim.vertex_count;

	//					for (int i = 0; i < vertex_count; i++)
	//					{
	//						Index idx = vertices[vertex_start_index + i];
	//						p->appendParticle(idx);
	//					}
	//				}
	//				else
	//				{}
	//			}
	//		}

	//		{
	//			// write point attributes

	//			const auto& attributes = point_attributes;
	//			const Size count = point_count;
	//			const GA_AttributeOwner owner = GA_ATTRIB_POINT;
	//			const auto range = gdp->getPointRange();

	//			for (auto attr_base : attributes)
	//			{
	//				if (attr_base->type == ValueType::Float)
	//				{
	//					using T = float;

	//					auto hio_attr = (const Attribute_<T>*)attr_base.get();
	//					GA_Attribute* A = gdp->addFloatTuple(owner, hio_attr->name.c_str(), hio_attr->tuple_size);
	//					A->setTypeInfo(to_enum(hio_attr->typeinfo));

	//					if (hio_attr->tuple_size == 1)
	//					{
	//						UT_ValArray<T> VA(count, count);
	//						memcpy(VA.array(), (const T*)&hio_attr->data()[0], sizeof(T) * count);
	//						gdp->setAttributeFromArray(A, range, VA);
	//					}
	//					else if (hio_attr->tuple_size == 2)
	//					{
	//						UT_ValArray<UT_Vector2T<T>> VA(count, count);
	//						memcpy(VA.array(), (const T*)&hio_attr->data()[0], sizeof(T) * count * 2);
	//						gdp->setAttributeFromArray(A, range, VA);
	//					}
	//					else if (hio_attr->tuple_size == 3)
	//					{
	//						UT_ValArray<UT_Vector3T<T>> VA(count, count);
	//						memcpy(VA.array(), (const T*)&hio_attr->data()[0], sizeof(T) * count * 3);
	//						gdp->setAttributeFromArray(A, range, VA);
	//					}
	//					else if (hio_attr->tuple_size == 4)
	//					{
	//						UT_ValArray<UT_Vector4T<T>> VA(count, count);
	//						memcpy(VA.array(), (const T*)&hio_attr->data()[0], sizeof(T) * count * 4);
	//						gdp->setAttributeFromArray(A, range, VA);
	//					}
	//				}
	//				else if (attr_base->type == ValueType::String)
	//				{
	//					auto hio_attr = (const Attribute_<std::string>*)attr_base.get();
	//					GA_Attribute* A = gdp->addStringTuple(owner, hio_attr->name.c_str(), hio_attr->tuple_size);
	//					A->setTypeInfo(to_enum(hio_attr->typeinfo));

	//					const GA_AIFStringTuple* tuple = A->getAIFStringTuple();

	//					for (int i = 0; i < count; i++)
	//					{
	//						const auto& hio_tuplle = hio_attr->getTuple(i);
	//						for (int x = 0; x < hio_tuplle.size(); x++)
	//						{
	//							tuple->setString(A, GA_Offset(i), hio_tuplle[x].data(), x);
	//						}
	//					}
	//				}
	//			}
	//		}

	//		{
	//			// write vertex attributes

	//			const auto& attributes = vertex_attributes;
	//			const Size count = vertex_count;
	//			const GA_AttributeOwner owner = GA_ATTRIB_VERTEX;
	//			const auto range = gdp->getVertexRange();

	//			for (auto attr_base : attributes)
	//			{
	//				if (attr_base->type == ValueType::Float)
	//				{
	//					using T = float;

	//					auto hio_attr = (const Attribute_<T>*)attr_base.get();
	//					GA_Attribute* A = gdp->addFloatTuple(owner, hio_attr->name.c_str(), hio_attr->tuple_size);
	//					A->setTypeInfo(to_enum(hio_attr->typeinfo));

	//					if (hio_attr->tuple_size == 1)
	//					{
	//						UT_ValArray<T> VA(count, count);
	//						memcpy(VA.array(), (const T*)&hio_attr->data()[0], sizeof(T) * count);
	//						gdp->setAttributeFromArray(A, range, VA);
	//					}
	//					else if (hio_attr->tuple_size == 2)
	//					{
	//						UT_ValArray<UT_Vector2T<T>> VA(count, count);
	//						memcpy(VA.array(), (const T*)&hio_attr->data()[0], sizeof(T) * count * 2);
	//						gdp->setAttributeFromArray(A, range, VA);
	//					}
	//					else if (hio_attr->tuple_size == 3)
	//					{
	//						UT_ValArray<UT_Vector3T<T>> VA(count, count);
	//						memcpy(VA.array(), (const T*)&hio_attr->data()[0], sizeof(T) * count * 3);
	//						gdp->setAttributeFromArray(A, range, VA);
	//					}
	//					else if (hio_attr->tuple_size == 4)
	//					{
	//						UT_ValArray<UT_Vector4T<T>> VA(count, count);
	//						memcpy(VA.array(), (const T*)&hio_attr->data()[0], sizeof(T) * count * 4);
	//						gdp->setAttributeFromArray(A, range, VA);
	//					}
	//				}
	//				else if (attr_base->type == ValueType::String)
	//				{
	//					auto hio_attr = (const Attribute_<std::string>*)attr_base.get();
	//					GA_Attribute* A = gdp->addStringTuple(owner, hio_attr->name.c_str(), hio_attr->tuple_size);
	//					A->setTypeInfo(to_enum(hio_attr->typeinfo));

	//					const GA_AIFStringTuple* tuple = A->getAIFStringTuple();

	//					for (int i = 0; i < count; i++)
	//					{
	//						const auto& hio_tuplle = hio_attr->getTuple(i);
	//						for (int x = 0; x < hio_tuplle.size(); x++)
	//						{
	//							tuple->setString(A, GA_Offset(i), hio_tuplle[x].data(), x);
	//						}
	//					}
	//				}
	//			}
	//		}

	//		{
	//			// write primitive attributes

	//			const auto& attributes = primitive_attributes;
	//			const Size count = prim_count;
	//			const GA_AttributeOwner owner = GA_ATTRIB_PRIMITIVE;
	//			const auto range = gdp->getPrimitiveRange();

	//			for (auto attr_base : attributes)
	//			{
	//				if (attr_base->type == ValueType::Float)
	//				{
	//					using T = float;

	//					auto hio_attr = (const Attribute_<T>*)attr_base.get();
	//					GA_Attribute* A = gdp->addFloatTuple(owner, hio_attr->name.c_str(), hio_attr->tuple_size);
	//					A->setTypeInfo(to_enum(hio_attr->typeinfo));

	//					if (hio_attr->tuple_size == 1)
	//					{
	//						UT_ValArray<T> VA(count, count);
	//						memcpy(VA.array(), (const T*)&hio_attr->data()[0], sizeof(T) * count);
	//						gdp->setAttributeFromArray(A, range, VA);
	//					}
	//					else if (hio_attr->tuple_size == 2)
	//					{
	//						UT_ValArray<UT_Vector2T<T>> VA(count, count);
	//						memcpy(VA.array(), (const T*)&hio_attr->data()[0], sizeof(T) * count * 2);
	//						gdp->setAttributeFromArray(A, range, VA);
	//					}
	//					else if (hio_attr->tuple_size == 3)
	//					{
	//						UT_ValArray<UT_Vector3T<T>> VA(count, count);
	//						memcpy(VA.array(), (const T*)&hio_attr->data()[0], sizeof(T) * count * 3);
	//						gdp->setAttributeFromArray(A, range, VA);
	//					}
	//					else if (hio_attr->tuple_size == 4)
	//					{
	//						UT_ValArray<UT_Vector4T<T>> VA(count, count);
	//						memcpy(VA.array(), (const T*)&hio_attr->data()[0], sizeof(T) * count * 4);
	//						gdp->setAttributeFromArray(A, range, VA);
	//					}
	//				}
	//				else if (attr_base->type == ValueType::String)
	//				{
	//					auto hio_attr = (const Attribute_<std::string>*)attr_base.get();
	//					GA_Attribute* A = gdp->addStringTuple(owner, hio_attr->name.c_str(), hio_attr->tuple_size);
	//					A->setTypeInfo(to_enum(hio_attr->typeinfo));

	//					const GA_AIFStringTuple* tuple = A->getAIFStringTuple();

	//					for (int i = 0; i < count; i++)
	//					{
	//						const auto& hio_tuplle = hio_attr->getTuple(i);
	//						for (int x = 0; x < hio_tuplle.size(); x++)
	//						{
	//							tuple->setString(A, GA_Offset(i), hio_tuplle[x].data(), x);
	//						}
	//					}
	//				}
	//			}
	//		}

	//		{
	//			// write detail attributes

	//			const auto& attributes = detail_attributes;
	//			const Size count = 1;
	//			const GA_AttributeOwner owner = GA_ATTRIB_DETAIL;
	//			const auto range = gdp->getGlobalRange();

	//			for (auto attr_base : attributes)
	//			{
	//				if (attr_base->type == ValueType::Float)
	//				{
	//					using T = float;

	//					auto hio_attr = (const Attribute_<T>*)attr_base.get();
	//					GA_Attribute* A = gdp->addFloatTuple(owner, hio_attr->name.c_str(), hio_attr->tuple_size);
	//					A->setTypeInfo(to_enum(hio_attr->typeinfo));

	//					if (hio_attr->tuple_size == 1)
	//					{
	//						UT_ValArray<T> VA(count, count);
	//						memcpy(VA.array(), (const T*)&hio_attr->data()[0], sizeof(T) * count);
	//						gdp->setAttributeFromArray(A, range, VA);
	//					}
	//					else if (hio_attr->tuple_size == 2)
	//					{
	//						UT_ValArray<UT_Vector2T<T>> VA(count, count);
	//						memcpy(VA.array(), (const T*)&hio_attr->data()[0], sizeof(T) * count * 2);
	//						gdp->setAttributeFromArray(A, range, VA);
	//					}
	//					else if (hio_attr->tuple_size == 3)
	//					{
	//						UT_ValArray<UT_Vector3T<T>> VA(count, count);
	//						memcpy(VA.array(), (const T*)&hio_attr->data()[0], sizeof(T) * count * 3);
	//						gdp->setAttributeFromArray(A, range, VA);
	//					}
	//					else if (hio_attr->tuple_size == 4)
	//					{
	//						UT_ValArray<UT_Vector4T<T>> VA(count, count);
	//						memcpy(VA.array(), (const T*)&hio_attr->data()[0], sizeof(T) * count * 4);
	//						gdp->setAttributeFromArray(A, range, VA);
	//					}
	//				}
	//				else if (attr_base->type == ValueType::String)
	//				{
	//					auto hio_attr = (const Attribute_<std::string>*)attr_base.get();
	//					GA_Attribute* A = gdp->addStringTuple(owner, hio_attr->name.c_str(), hio_attr->tuple_size);
	//					A->setTypeInfo(to_enum(hio_attr->typeinfo));

	//					const GA_AIFStringTuple* tuple = A->getAIFStringTuple();

	//					for (int i = 0; i < count; i++)
	//					{
	//						const auto& hio_tuplle = hio_attr->getTuple(i);
	//						for (int x = 0; x < hio_tuplle.size(); x++)
	//						{
	//							tuple->setString(A, GA_Offset(i), hio_tuplle[x].data(), x);
	//						}
	//					}
	//				}
	//			}
	//		}

	//		UT_StringArray errors;
	//		GA_SaveOptions opts;

	//		std::string _path = path;
	//		std::replace(_path.begin(), _path.end(), '\\', '/');

	//		auto res = gdp->save(_path.c_str(), &opts, &errors);
	//		if (!res.success())
	//		{
	//			for (auto s : errors)
	//				std::cerr << s << std::endl;
	//			return false;
	//		}

	//		return true;
	//	}
	//	catch (std::exception e)
	//	{
	//		std::cerr << e.what() << std::endl;
	//		return false;
	//	}
	}


	void Primitive::setPositions(const Vector3* data, Index offset, Size size)
	{
		Attrib P(prim()->getDetail().getP());
		P.setAttribValue<float>(data, offset + _prim->getVertexOffset(0), size);
	}

	void Primitive::positions(Vector3* out_data, Index offset, Size size)
	{
		Attrib P(prim()->getDetail().getP());
		P.attribValue<float>(out_data, offset + _prim->getVertexOffset(0), size);
	}

	hio::Vertex Primitive::vertex(Index index)
	{
		return Vertex(_prim->getVertexIndex(index));
	}

	hio::Vector3 Point::position(const Geometry& geo) const
	{
		return geo.geo().getPos3(index);
	}

	void Point::setPosition(Geometry& geo, const Vector3& P)
	{
		return geo.geo().setPos3(index, P);
	}

	Polygon::Polygon(GEO_Primitive* prim)
		: Primitive(prim)
	{
		if (prim->getTypeDef().getId() != Polygon::prim_typeid)
			throw std::runtime_error("Invalid cast");
	}

	Polygon::Polygon(const Primitive& cast)
		: Primitive(cast.prim())
	{
		if (cast.prim()->getTypeDef().getId() != Polygon::prim_typeid)
			throw std::runtime_error("Invalid cast");
	}

	hio::Vertex Polygon::addVertex(Point point)
	{
		auto vtx = poly()->appendVertex(point.number());
		return Vertex(vtx);
	}

	BezierCurve::BezierCurve(GEO_Primitive* prim)
		: Primitive(prim)
	{
		if (prim->getTypeDef().getId() != BezierCurve::prim_typeid)
			throw std::runtime_error("Invalid cast");
	}

	BezierCurve::BezierCurve(const Primitive& cast)
		: Primitive(cast.prim())
	{
		if (cast.prim()->getTypeDef().getId() != BezierCurve::prim_typeid)
			throw std::runtime_error("Invalid cast");
	}

	hio::Vertex BezierCurve::addVertex(Point point)
	{
		auto vtx = curve()->appendVertex(point.number());
		return Vertex(vtx);
	}

	NURBSCurve::NURBSCurve(GEO_Primitive* prim)
		: Primitive(prim)
	{
		if (prim->getTypeDef().getId() != NURBSCurve::prim_typeid)
			throw std::runtime_error("Invalid cast");
	}

	NURBSCurve::NURBSCurve(const Primitive& cast)
		: Primitive(cast.prim())
	{
		if (cast.prim()->getTypeDef().getId() != NURBSCurve::prim_typeid)
			throw std::runtime_error("Invalid cast");
	}

	hio::Vertex NURBSCurve::addVertex(Point point)
	{
		auto vtx = curve()->appendVertex(point.number());
		return Vertex(vtx);
	}

}
