import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Main Window Designer Component
const WindowDesigner = () => {
  const [materialSystems, setMaterialSystems] = useState([]);
  const [glassTypes, setGlassTypes] = useState([]);
  const [config, setConfig] = useState({
    width: 1200,
    height: 1400,
    opening_type: "casement",
    system_id: "",
    glass_id: "",
    leaves: 1,
    mullions: 0,
    transoms: 0
  });
  const [calculation, setCalculation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [initialized, setInitialized] = useState(false);

  // Opening type labels in Spanish
  const openingTypeLabels = {
    casement: "Batiente/Lateral",
    awning: "Proyectante/Superior", 
    turn_tilt: "Oscilobatiente",
    sliding: "Corredera",
    folding: "Plegable"
  };

  // Material type labels
  const materialTypeLabels = {
    aluminum: "Aluminio",
    upvc: "uPVC/PVC",
    wood: "Madera",
    steel: "Acero"
  };

  // Initialize sample data
  const initializeSampleData = async () => {
    try {
      await axios.get(`${API}/init-data`);
      setInitialized(true);
    } catch (error) {
      console.error("Error initializing data:", error);
    }
  };

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      try {
        if (!initialized) {
          await initializeSampleData();
        }
        
        const [systemsRes, glassRes] = await Promise.all([
          axios.get(`${API}/material-systems`),
          axios.get(`${API}/glass`)
        ]);
        
        setMaterialSystems(systemsRes.data);
        setGlassTypes(glassRes.data);
        
        // Set defaults
        if (systemsRes.data.length > 0 && !config.system_id) {
          setConfig(prev => ({ ...prev, system_id: systemsRes.data[0].id }));
        }
        if (glassRes.data.length > 0 && !config.glass_id) {
          setConfig(prev => ({ ...prev, glass_id: glassRes.data[0].id }));
        }
      } catch (error) {
        console.error("Error loading data:", error);
      }
    };

    loadData();
  }, [initialized]);

  // Calculate window when config changes
  useEffect(() => {
    if (config.system_id && config.glass_id) {
      calculateWindow();
    }
  }, [config]);

  const calculateWindow = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/calculate`, config);
      setCalculation(response.data);
    } catch (error) {
      console.error("Calculation error:", error);
      setCalculation(null);
    } finally {
      setLoading(false);
    }
  };

  const handleConfigChange = (field, value) => {
    setConfig(prev => ({ ...prev, [field]: value }));
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <div className="ml-4">
                <h1 className="text-2xl font-bold text-gray-900">RA Workshop</h1>
                <p className="text-sm text-gray-500">Diseño y Cotización de Ventanas/Puertas</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Configuration Panel */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Configuración de Ventana</h2>
            
            <div className="space-y-6">
              {/* Dimensions */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Ancho (mm)
                  </label>
                  <input
                    type="number"
                    value={config.width}
                    onChange={(e) => handleConfigChange('width', parseInt(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="300"
                    max="3000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Alto (mm)
                  </label>
                  <input
                    type="number"
                    value={config.height}
                    onChange={(e) => handleConfigChange('height', parseInt(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="300"
                    max="2500"
                  />
                </div>
              </div>

              {/* Opening Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tipo de Apertura
                </label>
                <select
                  value={config.opening_type}
                  onChange={(e) => handleConfigChange('opening_type', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {Object.entries(openingTypeLabels).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              </div>

              {/* Material System */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Sistema de Perfiles
                </label>
                <select
                  value={config.system_id}
                  onChange={(e) => handleConfigChange('system_id', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {materialSystems.map((system) => (
                    <option key={system.id} value={system.id}>
                      {system.name} ({materialTypeLabels[system.material_type]})
                    </option>
                  ))}
                </select>
              </div>

              {/* Glass Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tipo de Vidrio
                </label>
                <select
                  value={config.glass_id}
                  onChange={(e) => handleConfigChange('glass_id', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {glassTypes.map((glass) => (
                    <option key={glass.id} value={glass.id}>
                      {glass.description} (U={glass.u_value})
                    </option>
                  ))}
                </select>
              </div>

              {/* Additional Configuration */}
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Hojas
                  </label>
                  <input
                    type="number"
                    value={config.leaves}
                    onChange={(e) => handleConfigChange('leaves', parseInt(e.target.value) || 1)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="1"
                    max="4"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Travesaños
                  </label>
                  <input
                    type="number"
                    value={config.mullions}
                    onChange={(e) => handleConfigChange('mullions', parseInt(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="0"
                    max="3"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Montantes
                  </label>
                  <input
                    type="number"
                    value={config.transoms}
                    onChange={(e) => handleConfigChange('transoms', parseInt(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="0"
                    max="2"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Results Panel */}
          <div className="space-y-6">
            
            {/* Summary Card */}
            {calculation && (
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Resumen de Cotización</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-sm text-blue-600 font-medium">Precio Final</p>
                    <p className="text-2xl font-bold text-blue-900">
                      {formatCurrency(calculation.final_price)}
                    </p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <p className="text-sm text-green-600 font-medium">Área Vidrio</p>
                    <p className="text-xl font-bold text-green-900">
                      {calculation.glass_area.toFixed(2)} m²
                    </p>
                  </div>
                  <div className="bg-orange-50 p-4 rounded-lg">
                    <p className="text-sm text-orange-600 font-medium">Peso Total</p>
                    <p className="text-xl font-bold text-orange-900">
                      {calculation.weight.toFixed(1)} kg
                    </p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <p className="text-sm text-purple-600 font-medium">Materiales</p>
                    <p className="text-xl font-bold text-purple-900">
                      {formatCurrency(calculation.total_material_cost)}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* BOM Table */}
            {calculation && (
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Lista de Materiales (BOM)</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Descripción
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Cantidad
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Costo Unit.
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Total
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {calculation.bom_items.map((item, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-sm text-gray-900">
                            <div className="flex items-center">
                              <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full mr-2 ${
                                item.item_type === 'profile' ? 'bg-blue-100 text-blue-800' :
                                item.item_type === 'glass' ? 'bg-green-100 text-green-800' :
                                'bg-orange-100 text-orange-800'
                              }`}>
                                {item.item_type === 'profile' ? 'Perfil' :
                                 item.item_type === 'glass' ? 'Vidrio' : 'Herraje'}
                              </span>
                              {item.description}
                            </div>
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-500">
                            {item.quantity.toFixed(2)} {item.unit}
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-500">
                            {formatCurrency(item.unit_cost)}
                          </td>
                          <td className="px-4 py-3 text-sm font-medium text-gray-900">
                            {formatCurrency(item.total_cost)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot className="bg-gray-50">
                      <tr>
                        <td colSpan="3" className="px-4 py-3 text-sm font-medium text-gray-900">
                          Subtotal Materiales
                        </td>
                        <td className="px-4 py-3 text-sm font-bold text-gray-900">
                          {formatCurrency(calculation.total_material_cost)}
                        </td>
                      </tr>
                      <tr>
                        <td colSpan="3" className="px-4 py-3 text-sm font-medium text-gray-900">
                          Mano de Obra (10%)
                        </td>
                        <td className="px-4 py-3 text-sm font-bold text-gray-900">
                          {formatCurrency(calculation.labor_cost)}
                        </td>
                      </tr>
                      <tr>
                        <td colSpan="3" className="px-4 py-3 text-sm font-medium text-gray-900">
                          Margen ({calculation.margin_percent}%)
                        </td>
                        <td className="px-4 py-3 text-sm font-bold text-gray-900">
                          {formatCurrency(calculation.final_price - calculation.total_material_cost - calculation.labor_cost)}
                        </td>
                      </tr>
                      <tr className="border-t-2 border-gray-200">
                        <td colSpan="3" className="px-4 py-3 text-lg font-bold text-gray-900">
                          PRECIO FINAL
                        </td>
                        <td className="px-4 py-3 text-lg font-bold text-blue-600">
                          {formatCurrency(calculation.final_price)}
                        </td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </div>
            )}

            {/* Loading State */}
            {loading && (
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                  <p className="ml-4 text-gray-600">Calculando presupuesto...</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <WindowDesigner />
    </div>
  );
}

export default App;