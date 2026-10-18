import React, { useState } from 'react';
import { AlertCircle, X, Send, MapPin, Phone } from 'lucide-react';

interface SOSModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: {
    raw_sos: string;
    caller_contact?: string;
    location_name?: string;
    latitude?: number;
    longitude?: number;
  }) => Promise<void>;
}

const PRESET_SCENARIOS = [
  {
    title: 'Hospital Basement Inundation',
    tag: 'Medical Emergency',
    sos: 'CRITICAL: Riverside Care Hospital basement and ground floor flooded 2.3m. 5 elderly ICU patients on oxygen support. Power mains sparking, backup generator submerged. Need immediate aquatic rescue team with paramedics.',
    location: 'Riverside Care Hospital, Bharalu Ghat',
    lat: 26.1620,
    lng: 91.7480,
  },
  {
    title: 'School Bus Marooned in Underpass',
    tag: 'Children at Risk',
    sos: 'SOS: School bus trapped under submerged railway underpass on Zoo Road. 12 schoolchildren and driver trapped inside. Water level at 1.6m and rising rapidly. Urgent boat evacuation needed.',
    location: 'Zoo Road Railway Underpass',
    lat: 26.1510,
    lng: 91.7690,
  },
  {
    title: 'Residential Roof Structural Collapse',
    tag: 'Building Collapse',
    sos: 'URGENT: Brick house cracking in Anil Nagar lane 4 due to flood erosion. 4 family members including an 80yo grandmother stranded on tin roof. Water 1.9m outside with fast current.',
    location: 'Anil Nagar Lane 4, House 18',
    lat: 26.1575,
    lng: 91.7610,
  },
  {
    title: 'Slum Colony Embankment Breach',
    tag: 'Mass Evacuation',
    sos: 'HELP: Sudden embankment breach at Pandu slum cluster. Over 20 people including infants huddled on temple raised platform. Flood water 1.5m deep and contaminated. Require boats and relief kits.',
    location: 'Pandu Ghat Colony Temple Plinth',
    lat: 26.1650,
    lng: 91.7300,
  },
];

export const SOSModal: React.FC<SOSModalProps> = ({ isOpen, onClose, onSubmit }) => {
  const [rawSos, setRawSos] = useState('');
  const [caller, setCaller] = useState('+91-98765-43210');
  const [locationName, setLocationName] = useState('');
  const [lat, setLat] = useState<number | undefined>(undefined);
  const [lng, setLng] = useState<number | undefined>(undefined);
  const [submitting, setSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleApplyPreset = (preset: typeof PRESET_SCENARIOS[0]) => {
    setRawSos(preset.sos);
    setLocationName(preset.location);
    setLat(preset.lat);
    setLng(preset.lng);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!rawSos.trim()) return;

    setSubmitting(true);
    try {
      await onSubmit({
        raw_sos: rawSos,
        caller_contact: caller,
        location_name: locationName || undefined,
        latitude: lat,
        longitude: lng,
      });
      onClose();
    } catch (err) {
      console.error('Failed to submit SOS:', err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[2000] flex items-center justify-center p-4 bg-black/75">
      <div className="bg-slate-900 border border-slate-700 rounded-lg w-full max-w-2xl shadow-xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="p-3.5 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded bg-red-600/20 border border-red-500/30 flex items-center justify-center text-red-400">
              <AlertCircle className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-xs font-semibold text-slate-100">Emergency Incident Intake</h3>
              <p className="text-[11px] text-slate-400">Triggers the 6-agent autonomous response pipeline</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded text-slate-400 hover:text-slate-200 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-4 overflow-y-auto space-y-3.5">
          {/* Preset Test Scenarios */}
          <div>
            <div className="flex items-center justify-between mb-1.5 text-xs">
              <span className="font-medium text-slate-300">Quick Test Scenarios:</span>
              <span className="text-[11px] text-slate-500">Click to autofill incident</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {PRESET_SCENARIOS.map((preset, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleApplyPreset(preset)}
                  className="text-left p-2 rounded border border-slate-800 bg-slate-950 hover:border-slate-700 transition-colors"
                >
                  <div className="flex items-center justify-between text-[10px] mb-1">
                    <span className="text-slate-200 font-medium">{preset.title}</span>
                    <span className="bg-slate-900 text-slate-400 px-1 rounded border border-slate-800">{preset.tag}</span>
                  </div>
                  <p className="text-[11px] text-slate-400 line-clamp-2 italic">"{preset.sos}"</p>
                </button>
              ))}
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-3 pt-2 border-t border-slate-800">
            <div>
              <label className="block text-xs font-medium text-slate-200 mb-1">
                Distress Transmission / SOS Message *
              </label>
              <textarea
                required
                rows={3}
                value={rawSos}
                onChange={(e) => setRawSos(e.target.value)}
                placeholder="Describe the emergency: water depth, victim count (elderly, children, injured), hazards, location..."
                className="w-full bg-slate-950 border border-slate-800 focus:border-slate-600 rounded p-2.5 text-xs text-slate-100 placeholder:text-slate-600 focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] text-slate-400 mb-1 flex items-center gap-1">
                  <MapPin className="w-3 h-3 text-slate-400" /> Location / Landmark
                </label>
                <input
                  type="text"
                  value={locationName}
                  onChange={(e) => setLocationName(e.target.value)}
                  placeholder="e.g. Bharalu Riverbank near Overpass"
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-xs text-slate-100 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-[11px] text-slate-400 mb-1 flex items-center gap-1">
                  <Phone className="w-3 h-3 text-slate-400" /> Caller Contact
                </label>
                <input
                  type="text"
                  value={caller}
                  onChange={(e) => setCaller(e.target.value)}
                  placeholder="+91-98765-43210"
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-xs text-slate-100 focus:outline-none"
                />
              </div>
            </div>

            {/* Coordinates */}
            <div className="grid grid-cols-2 gap-3 text-slate-400 text-xs font-mono">
              <div>
                <span className="text-[10px]">Latitude (Optional):</span>
                <input
                  type="number"
                  step="0.0001"
                  value={lat ?? ''}
                  onChange={(e) => setLat(e.target.value ? parseFloat(e.target.value) : undefined)}
                  placeholder="26.1550"
                  className="w-full bg-slate-950 border border-slate-800 rounded p-1.5 text-xs text-slate-100 focus:outline-none"
                />
              </div>
              <div>
                <span className="text-[10px]">Longitude (Optional):</span>
                <input
                  type="number"
                  step="0.0001"
                  value={lng ?? ''}
                  onChange={(e) => setLng(e.target.value ? parseFloat(e.target.value) : undefined)}
                  placeholder="91.7500"
                  className="w-full bg-slate-950 border border-slate-800 rounded p-1.5 text-xs text-slate-100 focus:outline-none"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-800">
              <button
                type="button"
                onClick={onClose}
                className="px-3.5 py-1.5 rounded text-xs font-medium text-slate-400 hover:text-slate-200 bg-slate-950 border border-slate-800 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting || !rawSos.trim()}
                className="flex items-center gap-1.5 px-4 py-1.5 rounded text-xs font-medium text-white bg-red-600 hover:bg-red-500 border border-red-500/30 transition-colors disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5" />
                <span>{submitting ? 'Executing Pipeline...' : 'Submit SOS'}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
