#include <iostream>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
#include <pybind11/numpy.h>

#include "hio.h"

using namespace hio;

namespace py = pybind11;

#define DEFINE_VECTOR_PROP(CLS, NAME) \
	.def_property(#NAME, [](const CLS& self) -> float { return self.NAME(); }, [](CLS& self, float v) { self.NAME() = v; }, py::return_value_policy::copy)


PYBIND11_MODULE(CMAKE_PYMODULE_NAME, m) {

	py::enum_<AttribType> attrtype(m, "AttribType");
	attrtype
		.value("Point", AttribType::Point)
		.value("Prim", AttribType::Prim)
		.value("Vertex", AttribType::Vertex)
		.value("Global", AttribType::Global)
		;

	py::enum_<AttribData> attrdata(m, "AttribData");
	attrdata
		.value("Float", AttribData::Float)
		.value("Int", AttribData::Int)
		.value("String", AttribData::String)
		.value("Invalid", AttribData::Invalid)
		;

	py::enum_<TypeInfo> typeinfo(m, "TypeInfo");
	typeinfo
		.value("Point", TypeInfo::Point)
		.value("Vector", TypeInfo::Vector)
		.value("Normal", TypeInfo::Normal)
		.value("Color", TypeInfo::Color)
		.value("Matrix", TypeInfo::Matrix)
		.value("Quaternion", TypeInfo::Quaternion)
		.value("TextureCoord", TypeInfo::TextureCoord)
		.value("Value", TypeInfo::Value)
		;

	py::enum_<PrimitiveTypes> primtype(m, "PrimitiveTypes");
	primtype
		.value("Poly", PrimitiveTypes::Poly)
		.value("NURBSCurve", PrimitiveTypes::NURBSCurve)
		.value("BezierCurve", PrimitiveTypes::BezierCurve)
		;

	py::class_<Vector2> vector2(m, "Vector2");
	vector2
		.def(py::init<float, float>(), py::arg("x") = 0, py::arg("y") = 0)
		DEFINE_VECTOR_PROP(Vector2, x)
		DEFINE_VECTOR_PROP(Vector2, y)
		;

	py::class_<Vector3> vector3(m, "Vector3");
	vector3
		.def(py::init<float, float, float>(), py::arg("x") = 0, py::arg("y") = 0, py::arg("z") = 0)
		DEFINE_VECTOR_PROP(Vector3, x)
		DEFINE_VECTOR_PROP(Vector3, y)
		DEFINE_VECTOR_PROP(Vector3, z)
		;

	py::class_<Vector4> vector4(m, "Vector4");
	vector4
		.def(py::init<float, float, float, float>(), py::arg("x") = 0, py::arg("y") = 0, py::arg("z") = 0, py::arg("w") = 0)
		DEFINE_VECTOR_PROP(Vector4, x)
		DEFINE_VECTOR_PROP(Vector4, y)
		DEFINE_VECTOR_PROP(Vector4, z)
		DEFINE_VECTOR_PROP(Vector4, w)
		;

	py::class_<Attrib> attr(m, "Attrib");
	attr
		.def(py::init<>())
		.def("name", &Attrib::name)

		.def("size", &Attrib::size)
		.def("tupleSize", &Attrib::tupleSize)

		.def("type", &Attrib::type)
		.def("dataType", &Attrib::dataType)
		.def("typeInfo", &Attrib::typeInfo)

		.def("attribValue", [](const Attrib& self, Index offset = 0, Size size = -1) -> py::object
		{
			if (size < 0)
				size = self.size() - offset;

			if (self.dataType() == AttribData::Float)
			{
				py::array_t<float> arr(std::vector<Size>{ size, self.tupleSize() });
				self.attribValue<float>(arr.mutable_data(), offset, size);
				return arr;
			}
			else if (self.dataType() == AttribData::Int)
			{
				py::array_t<int> arr(std::vector<Size>{ size, self.tupleSize() });
				self.attribValue<int>(arr.mutable_data(), offset, size);
				return arr;
			}
			else if (self.dataType() == AttribData::String)
			{
				py::list arr;
				
				std::vector<std::string> str;
				str.resize(size);

				self.attribValue<std::string>(&str[0], offset, size);

				for (auto it : str)
					arr.append(it);
				
				return arr;
			}

			return py::none();

		}, py::arg("offset") = 0, py::arg("size") = -1)

		.def("setAttribValue", [](Attrib& self, const py::array_t<float>& data, Index offset = 0, Size size = -1) {
			auto tuple_size = data.shape()[1];

			if (self.tupleSize() != tuple_size)
				throw std::runtime_error("Tuple size mismatch");

			if (size < 0)
				size = self.size() - offset;

			self.setAttribValue<float>(data.data(), offset, size);
		}, py::arg("data"), py::arg("offset") = 0, py::arg("size") = -1)

		.def("setAttribValue", [](Attrib& self, const py::array_t<float>& data, Index offset = 0, Size size = -1) {
			auto tuple_size = data.shape()[1];

			if (self.tupleSize() != tuple_size)
				throw std::runtime_error("Tuple size mismatch");

			if (size < 0)
				size = self.size() - offset;

			self.setAttribValue<int>(data.data(), offset, size);
		}, py::arg("data"), py::arg("offset") = 0, py::arg("size") = -1)

		.def("setAttribValue", [](Attrib& self, py::list data, Index offset = 0, Size size = -1) {
			if (size < 0)
				size = self.size() - offset;

			std::vector<std::string> arr;
			for (int i = 0; i < data.size(); i++)
				arr.push_back(py::cast<std::string>(data[i]));

			self.setAttribValue<std::string>(arr.data(), offset, size);
		}, py::arg("data"), py::arg("offset") = 0, py::arg("size") = -1)

		;

	py::class_<Attrib_<float>, Attrib> float_attr(m, "FloatAttrib");
	py::class_<Attrib_<int>, Attrib> int_attr(m, "IntAttrib");
	py::class_<Attrib_<std::string>, Attrib> string_attr(m, "StringAttrib");

	py::class_<Point> point(m, "Point");
	point
		.def(py::init<Index>())
		.def("number", &Point::number)
		.def("position", &Point::position)
		.def("setPosition", &Point::setPosition)
		;

	py::class_<Vertex> vert(m, "Vertex");
	vert
		.def("number", &Vertex::number)
		;

	py::class_<Primitive> prim(m, "Primitive");
	prim
		.def("number", &Primitive::number)
		.def("vertexStartIndex", &Primitive::vertexStartIndex)
		.def("vertexCount", &Primitive::vertexCount)

		.def("vertex", &Primitive::vertex)

		.def("positions", [](Primitive& self) {
			py::array_t<float> arr(std::vector<Size>{ self.vertexCount(), 3 });
			self.positions((Vector3*)arr.mutable_data(), 0, self.vertexCount());
			return arr;
		})
		.def("setPositions", [](Primitive& self, const py::array_t<float>& data) {
			auto tuple_size = data.shape()[1];
			auto size = data.shape()[0];

			if (3 != tuple_size)
				throw std::runtime_error("Tuple size mismatch");

			if (size > self.vertexCount())
				throw std::runtime_error("Index out of range");

			self.setPositions((const Vector3*)data.data(), 0, size);
		})
		;

	py::class_<Polygon, Primitive> poly(m, "Polygon");
	poly
		.def(py::init<Primitive>())
		.def("addVertex", &Polygon::addVertex)
		.def("isClosed", &Polygon::isClosed)
		.def("setIsClosed", &Polygon::setIsClosed)
		;

	py::class_<BezierCurve, Primitive> bezier_curve(m, "BezierCurve");
	bezier_curve
		.def(py::init<Primitive>())
		.def("addVertex", &BezierCurve::addVertex)
		.def("isClosed", &BezierCurve::isClosed)
		.def("setIsClosed", &BezierCurve::setIsClosed)
		;

	py::class_<NURBSCurve, Primitive> nurbs_curve(m, "NURBSCurve");
	nurbs_curve
		.def(py::init<Primitive>())
		.def("addVertex", &NURBSCurve::addVertex)
		.def("isClosed", &NURBSCurve::isClosed)
		.def("setIsClosed", &NURBSCurve::setIsClosed)
		;

	py::class_<Geometry> geometry(m, "Geometry");
	geometry
		.def(py::init<>())
		.def("clear", &Geometry::clear)
		.def("getNumPoints", &Geometry::getNumPoints)
		.def("getNumVertices", &Geometry::getNumVertices)
		.def("getNumPrimitives", &Geometry::getNumPrimitives)

		.def("createPoint", &Geometry::createPoint)
		.def("createPoints", py::overload_cast<Size>(&Geometry::createPoints))
		.def("createPoints", [](Geometry& self, const py::array_t<float>& positions) {
			assert(positions.shape()[1] == 3);
			int N = positions.shape()[0];
			return self.createPoints(N, (const Vector3*)positions.data());
		})

		.def("point", &Geometry::point)
		.def("points", [](const Geometry& self) {
			py::array_t<float> arr(std::vector<Size>{ self.getNumPoints(), 3 });
			auto A = self.geo().getP();
			const GA_AIFTuple* tuple = A->getAIFTuple();
			tuple->getRange(A, self.geo().getPointRange(), arr.mutable_data(), 0, 3);
			return arr;
		})

		.def("prim", &Geometry::prim)
		.def("prims", &Geometry::prims)

		.def("createPolygon", &Geometry::createPolygon,
			py::arg("num_vertices") = 0, py::arg("is_closed") = true)
		.def("createPolygons", [](Geometry& self, const py::array_t<float>& positions, const py::array_t<Size>& vertex_counts, bool closed) {
			if (positions.shape()[1] != 3)
				throw std::runtime_error("`positions` shape must be (N, 3)");

			return self.createPolygons(positions.shape()[0], (const Vector3*)positions.data(),
				vertex_counts.size(), vertex_counts.data(),
				closed);
		}, py::arg("positions"), py::arg("vertex_counts"), py::arg("closed") = true)
		
		.def("createPolygons", [](Geometry& self, const py::array_t<float>& positions, const py::array_t<Index>& vertices, const py::array_t<Size>& vertex_counts, bool closed) {
			if (positions.shape()[1] != 3)
				throw std::runtime_error("`positions` shape must be (N, 3)");

			return self.createPolygons(positions.shape()[0], (const Vector3*)positions.data(),
				vertices.size(), vertices.data(),
				vertex_counts.size(), vertex_counts.data(),
				closed);
		}, py::arg("positions"), py::arg("vertices"), py::arg("vertex_counts"), py::arg("closed") = true)

		.def("createBezierCurve", &Geometry::createBezierCurve,
			py::arg("num_vertices"), py::arg("is_closed") = false, py::arg("order") = 4)
		.def("createNURBSCurve", &Geometry::createNURBSCurve,
			py::arg("num_vertices"), py::arg("is_closed") = false, py::arg("order") = 4, py::arg("_interp_ends") = -1)

		.def("pointAttribs", &Geometry::pointAttribs)
		.def("primAttribs", &Geometry::primAttribs)
		.def("vertexAttribs", &Geometry::vertexAttribs)
		.def("globalAttribs", &Geometry::globalAttribs)

		.def("addFloatAttrib", [](Geometry& self, AttribType type, const std::string& name, const std::vector<float>& default_value, TypeInfo typeinfo) {
			return self.addAttrib<float>(type, name, default_value, typeinfo);
		}, py::return_value_policy::copy)

		.def("addIntAttrib", [](Geometry& self, AttribType type, const std::string& name, const std::vector<int>& default_value, TypeInfo typeinfo) {
			return self.addAttrib<int>(type, name, default_value, typeinfo);
		}, py::return_value_policy::copy)

		.def("addStringAttrib", [](Geometry& self, AttribType type, const std::string& name, TypeInfo typeinfo) {
			return self.addAttrib<std::string>(type, name, {""}, typeinfo);
		}, py::return_value_policy::copy)
		
		.def("findPointAttrib", [](const Geometry& self, const std::string& name) -> py::object {
			auto attr = self.findPointAttrib(name);
			if (!attr) return py::none();
			return py::cast(attr);
		}, py::return_value_policy::copy)

		.def("findPrimAttrib", [](const Geometry& self, const std::string& name) -> py::object {
			auto attr = self.findPrimAttrib(name);
			if (!attr) return py::none();
			return py::cast(attr);
		}, py::return_value_policy::copy)

		.def("findVertexAttrib", [](const Geometry& self, const std::string& name) -> py::object {
			auto attr = self.findVertexAttrib(name);
			if (!attr) return py::none();
			return py::cast(attr);
		}, py::return_value_policy::copy)

		.def("findGlobalAttrib", [](const Geometry& self, const std::string& name) -> py::object {
			auto attr = self.findGlobalAttrib(name);
			if (!attr) return py::none();
			return py::cast(attr);
		}, py::return_value_policy::copy)

		.def("load", &Geometry::load)
		.def("save", &Geometry::save)

		.def("_dataByType", [](Geometry& self, std::vector<PrimitiveTypes> types) {
			{
				GA_PrimitiveGroup *grp = self.geo().newInternalPrimitiveGroup();

				static GA_PrimitiveTypeId_tag _tag;

				for (auto prim : self.prims())
				{
					bool found = false;

					PrimitiveTypes prim_type = Enum2Enum(prim.prim()->getTypeDef().getId().get(), _tag);

					for (auto t : types)
					{
						if (t == prim_type)
						{
							found = true;
							break;
						}
					}

					if (!found)
					{
						grp->addIndex(prim.number());
					}
				}

				self.geo().deletePrimitives(*grp, true);
				self.geo().destroyPrimitiveGroup(grp);
			}

			auto dict = py::dict();

			std::vector<Primitive> prims;
			prims.reserve(self.getNumPrimitives());

			for (auto prim : self.prims())
			{
				prims.push_back(prim);
			}

			py::list _prims;

			std::vector<Index> vertices;
			std::vector<Index> vertices_lut;

			std::vector<Index> vertex_start_index;
			std::vector<Size> vertex_count;

			vertices.reserve(self.getNumVertices());
			vertices_lut.reserve(self.getNumVertices());

			vertex_start_index.reserve(self.getNumPrimitives());
			vertex_count.reserve(self.getNumPrimitives());

			for (auto prim : prims)
			{
				auto vtxs = prim.vertices();
				vertices.insert(vertices.end(), vtxs.begin(), vtxs.end());
				vertex_start_index.emplace_back(prim.vertexStartIndex());
				vertex_count.emplace_back(prim.vertexCount());

				auto s = prim.vertexStartIndex();
				for (int i = 0; i < prim.vertexCount(); i++)
				{
					vertices_lut.emplace_back(s + i);
				}

				if (prim.prim()->getTypeDef().getId() == Polygon::prim_typeid)
				{
					_prims.append(Polygon(prim));
				}
			}

			dict["prims"] = _prims;

			dict["vertices"] = py::array_t<Index>(vertices.size(), vertices.data());
			dict["vertices_lut"] = py::array_t<Index>(vertices_lut.size(), vertices_lut.data());
			dict["vertex_start_index"] = py::array_t<Index>(vertex_start_index.size(), vertex_start_index.data());
			dict["vertex_count"] = py::array_t<Size>(vertex_count.size(), vertex_count.data());
						return dict;
		})
	;
}

//#define CASE_ATTR_TYPE(TYPE, VALUE) \
//case Type2Enum<TYPE>::value: return py::cast((const Attribute_<TYPE>*)VALUE.get())
//
/////
//
//template <typename T, typename CLS>
//void def_attr_data(T, CLS& pyclass)
//{
//	pyclass.def("data", [](const Attribute_<T> &p) {
//		return py::array_t<T>(std::vector<size_t>{ p.size(), p.tuple_size }, (const float*)p.data().data());
//	});
//}
//
//template <typename CLS>
//void def_attr_data(std::string, CLS& pyclass)
//{
//	pyclass.def("data", [](const Attribute_<std::string> &p) {
//		return p.data();
//	});
//}
//
/////
//
//template <typename T>
//void def_attr_variants(pybind11::module& m, const std::string& name)
//{
//	py::class_<Attribute_<T>, std::shared_ptr<Attribute_<T>>, Attribute> attr(m, name.c_str());
//	attr
//		.def(py::init<uint8_t, std::string, TypeInfo>(),
//			py::arg("tuple_size"), py::arg("name"), py::arg("typeinfo") = TypeInfo::Value)
//		.def_readonly("name", &Attribute_<T>::name)
//		.def_readonly("typeinfo", &Attribute_<T>::typeinfo)
//		.def_readonly("tuple_size", &Attribute_<T>::tuple_size)
//		.def("append", (void (Attribute_<T>::*)(const std::vector<T>&)) &Attribute_<T>::append)
//		.def("getTuple", &Attribute_<T>::getTuple)
//		.def("resize", &Attribute_<T>::resize)
//		.def("size", &Attribute_<T>::size)
//		.def("clear", &Attribute_<T>::clear)
//		.def("validate", &Attribute_<T>::validate)
//		.def("__repr__", [name](const Attribute_<T> &p) {
//			return name + "(name:" + p.name + " tuple_size:" + std::to_string(p.tuple_size) + ")";
//		})
//	;
//
//	def_attr_data(T(), attr);
//}
//
//PYBIND11_MODULE(_hio, m) {
//
//	//PYBIND11_NUMPY_DTYPE(Vector2, x, y);
//	//PYBIND11_NUMPY_DTYPE(Vector3, x, y, z);
//	//PYBIND11_NUMPY_DTYPE(Vector4, x, y, z, w);
//
//	py::bind_vector<std::vector<std::shared_ptr<Attribute>>>(m, "AttributeArray");
//
//	py::enum_<PrimType> primtype(m, "PrimType");
//	primtype
//		.value("Polygon", PrimType::Polygon)
//		.value("NURBS", PrimType::NURBS)
//		.value("Bezier", PrimType::Bezier)
//		.value("Particle", PrimType::Particle)
//		.value("Unsupported", PrimType::Unsupported)
//		;
//
//	py::enum_<TypeInfo> typeinfo(m, "TypeInfo");
//	typeinfo
//		.value("Point", TypeInfo::Point)
//		.value("Vector", TypeInfo::Vector)
//		.value("Normal", TypeInfo::Normal)
//		.value("Color", TypeInfo::Color)
//		.value("Matrix", TypeInfo::Matrix)
//		.value("Quaternion", TypeInfo::Quaternion)
//		.value("TextureCoord", TypeInfo::TextureCoord)
//		.value("Value", TypeInfo::Value)
//		;
//
//	///
//
//	py::class_<Vector2> vector2(m, "Vector2");
//	vector2
//		.def(py::init<float, float>(), py::arg("x") = 0, py::arg("y") = 0)
//		.def_readwrite("x", &Vector2::x)
//		.def_readwrite("y", &Vector2::y)
//		.def("__repr__", [](const Vector2& p) {
//			return "Vector2(x:" + std::to_string(p.x) 
//				+ ", y:" + std::to_string(p.y)
//				+ ")";
//		})
//		.def("to_tuple", [](const Vector2& p) {
//			return py::make_tuple(p.x, p.y);
//		})
//		;
//
//	py::class_<Vector3> vector3(m, "Vector3");
//	vector3
//		.def(py::init<float, float, float>(), 
//			py::arg("x") = 0,
//			py::arg("y") = 0,
//			py::arg("z") = 0)
//		.def_readwrite("x", &Vector3::x)
//		.def_readwrite("y", &Vector3::y)
//		.def_readwrite("z", &Vector3::z)
//		.def("__repr__", [](const Vector3& p) {
//			return "Vector3(x:" + std::to_string(p.x)
//				+ ", y:" + std::to_string(p.y)
//				+ ", z:" + std::to_string(p.z)
//				+ ")";
//		})
//		.def("to_tuple", [](const Vector3& p) {
//			return py::make_tuple(p.x, p.y, p.z);
//		})
//		;
//
//	py::class_<Vector4> vector4(m, "Vector4");
//	vector4
//		.def(py::init<float, float, float, float>(),
//			py::arg("x") = 0,
//			py::arg("y") = 0,
//			py::arg("z") = 0,
//			py::arg("w") = 0)
//		.def_readwrite("x", &Vector4::x)
//		.def_readwrite("y", &Vector4::y)
//		.def_readwrite("z", &Vector4::z)
//		.def_readwrite("w", &Vector4::w)
//		.def("__repr__", [](const Vector4& p) {
//			return "Vector4(x:" + std::to_string(p.x)
//				+ ", y:" + std::to_string(p.y)
//				+ ", z:" + std::to_string(p.z)
//				+ ", w:" + std::to_string(p.w)
//				+ ")";
//		})
//		.def("to_tuple", [](const Vector4& p) {
//			return py::make_tuple(p.x, p.y, p.z, p.w);
//		})
//
//		;
//
//	///
//
//	py::class_<Attribute, std::shared_ptr<Attribute>> attribute(m, "Attribute");
//	attribute
//		.def_readonly("name", &Attribute::name)
//		.def_readonly("typeinfo", &Attribute::typeinfo)
//		;
//
//	///
//
//	def_attr_variants<float>(m, "FloatAttribute");
//	def_attr_variants<std::string>(m, "StringAttribute");
//	
//	///
//
//	py::class_<Primitive> primitive(m, "Primitive");
//	primitive
//		.def_readonly("type", &Primitive::type)
//		.def_readonly("vertex_start_index", &Primitive::vertex_start_index)
//		.def_readonly("vertex_count", &Primitive::vertex_count)
//		.def_readwrite("closed", &Primitive::closed)
//		.def_readwrite("order", &Primitive::order)
//		;
//
//	/////
//
//	py::class_<Geometry> geometry(m, "Geometry");
//	geometry
//		.def(py::init<>())
//		.def("getNumPoints", &Geometry::getNumPoints)
//		.def("getNumVertices", &Geometry::getNumVertices)
//		.def("getNumPrimitives", &Geometry::getNumPrimitives)
//
//		.def("getPoints", [](const Geometry& self) {
//			return py::array_t<float>(std::vector<size_t>{ self.points.size(), 3 }, (const float*)self.points.data());
//		})
//		.def("getVertices", [](const Geometry& self) {
//			return py::array_t<Index>(self.vertices.size(), self.vertices.data());
//		})
//		.def("getPrimitives", &Geometry::getPrimitives)
//
//		.def("getPrimitivesByType", [](const Geometry& self, std::vector<PrimType> filter = {}) {
//			std::vector<Index> vertices;
//			std::vector<Index> vertices_lut;
//
//			std::vector<PrimType> type;
//			std::vector<Index> vertex_start_index;
//			std::vector<Size> vertex_count;
//			std::vector<uint8_t> closed;
//
//			vertices.reserve(self.getNumVertices());
//			vertices_lut.reserve(self.getNumVertices());
//
//			type.reserve(self.getNumPrimitives());
//			vertex_start_index.reserve(self.getNumPrimitives());
//			vertex_count.reserve(self.getNumPrimitives());
//			closed.reserve(self.getNumPrimitives());
//
//			if (filter.empty())
//			{
//				for (int i = 0; i < self.getNumPrimitives(); i++)
//				{
//					const Primitive& prim = self.getPrimitive(i);
//					type.push_back(prim.type);
//					vertex_start_index.push_back(prim.vertex_start_index);
//					vertex_count.push_back(prim.vertex_count);
//					closed.push_back(prim.closed);
//				}
//
//				vertices.assign(self.vertices.begin(), self.vertices.end());
//
//				for (int i = 0; i < self.vertices.size(); i++)
//					vertices_lut.push_back(i);
//			}
//			else
//			{
//				const Index* src_vertices_data = self.vertices.data();
//
//				for (int i = 0; i < self.getNumPrimitives(); i++)
//				{
//					bool found = false;
//					const Primitive& prim = self.getPrimitive(i);
//
//					for (auto filter_prim_type : filter)
//					{
//						if (prim.type == filter_prim_type)
//						{
//							found = true;
//							break;
//						}
//					}
//
//					if (!found) continue;
//
//					Index filterd_vertex_start_index = vertices.size();
//
//					type.push_back(prim.type);
//					vertex_start_index.push_back(filterd_vertex_start_index);
//					vertex_count.push_back(prim.vertex_count);
//					closed.push_back(prim.closed);
//
//					Index src_vertex_start_index = prim.vertex_start_index;
//
//					for (int n = 0; n < prim.vertex_count; n++)
//					{
//						Index idx = src_vertices_data[src_vertex_start_index + n];
//						vertices.push_back(idx);
//						vertices_lut.push_back(src_vertex_start_index + n);
//					}
//				}
//			}
//
//			auto dict = py::dict();
//
//			dict["vertices"] = py::array_t<Index>(vertices.size(), vertices.data());
//			dict["vertices_lut"] = py::array_t<Index>(vertices_lut.size(), vertices_lut.data());
//
//			dict["type"] = py::array_t<PrimType>(type.size(), type.data());
//			dict["vertex_start_index"] = py::array_t<Index>(vertex_start_index.size(), vertex_start_index.data());
//			dict["vertex_count"] = py::array_t<Size>(vertex_count.size(), vertex_count.data());
//			dict["closed"] = py::array_t<uint8_t>(closed.size(), closed.data());
//
//			return dict;
//		}, py::arg("filter") = std::vector<PrimType>())
//
//		.def("createPoint", [](Geometry& self, float x, float y, float z) {
//			auto res = self.createPoint(x, y, z);
//			return py::make_tuple(res.first, res.second);
//		},	py::arg("x") = 0, py::arg("y") = 0, py::arg("z") = 0)
//
//		.def("createPrimitive", [](Geometry& self, PrimType type, py::array_t<Index> vertices) {
//			py::buffer_info buf = vertices.request();
//
//			assert(buf.ndim == 1);
//			
//			auto ptr = (Index*)buf.ptr;
//			auto res = self.createPrimitive(type, ptr, ptr + buf.size);
//			auto prim = res.second;
//			return py::make_tuple(res.first, res.second);
//		})
//
//		//.def("getPoints", &Geometry::getPoints)
//		//.def("getVertices", &Geometry::getVertices)
//		//.def("getPrimitives", &Geometry::getPrimitives)
//
//		.def_readwrite("point_attributes", &Geometry::point_attributes, py::return_value_policy::reference_internal)
//		.def_readwrite("vertex_attributes", &Geometry::vertex_attributes, py::return_value_policy::reference_internal)
//		.def_readwrite("primitive_attributes", &Geometry::primitive_attributes, py::return_value_policy::reference_internal)
//		.def_readwrite("detail_attributes", &Geometry::detail_attributes, py::return_value_policy::reference_internal)
//
//		.def("load", &Geometry::load)
//		.def("save", &Geometry::save)
//		;
//	
//}
