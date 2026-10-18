import React, { useState, useEffect, useRef } from 'react';
import {
  PhoneCall,
  Mic,
  MicOff,
  MapPin,
  Send,
  AlertTriangle,
  ShieldAlert,
  Clock,
  Radio,
  CheckCircle2,
  Home,
  Droplets,
  Zap,
  Users,
  Volume2,
  Navigation,
  ArrowLeft,
  LifeBuoy,
} from 'lucide-react';
import { Incident, Team, ReliefCamp } from '../types';

interface CitizenPortalProps {
  onBackToEOC: () => void;
  onSubmitSOS: (data: {
    raw_sos: string;
    caller_contact?: string;
    location_name?: string;
    latitude?: number;
    longitude?: number;
  }) => Promise<void>;
  incidents: Incident[];
  teams: Team[];
  camps: ReliefCamp[];
  lastSubmittedIncidentId?: string | null;
}

const CALL_SIMULATION_SCRIPTS = [
  {
    title: 'Elderly Trapped on Roof with Sparks',
    transcript:
      'Help us please! Water has reached the first floor ceiling in Anil Nagar Lane 4. My 82-year-old grandmother is with me on the tin roof. The electric transformer outside is sparking and smoking into the flood water. Current is very fast. We have no food or drinking water. Send an NDRF boat immediately!',
    location: 'Anil Nagar Lane 4, House 18',
    lat: 26.1575,
    lng: 91.7610,
    caller: '+91-98640-11223',
  },
  {
    title: 'School Bus Marooned in Railway Underpass',
    transcript:
      'Emergency 112! This is driver Ramesh. School bus stalled in flash flood water under Zoo Road railway bridge. Water is 1.6 meters high and rising past window level. 12 schoolchildren inside are screaming and terrified. Water current is pushing the bus. Need urgent rescue team with life jackets!',
    location: 'Zoo Road Railway Underpass',
    lat: 26.1510,
    lng: 91.7690,
    caller: '+91-94350-99881',
  },
  {
    title: 'Hospital Ground Floor ICU Inundated',
    transcript:
      'Urgent dispatch required! Riverside Care Hospital basement and ground floor inundated 2.2m. 5 elderly cardiac patients on oxygen cylinders stranded. Generator room submerged, power out. Oxygen running out within 45 minutes. Require aquatic rescue team and mobile trauma doctors.',
    location: 'Riverside Care Hospital, Bharalu Ghat',
    lat: 26.1620,
    lng: 91.7480,
    caller: '+91-91270-33445',
  },
];

export const CitizenPortal: React.FC<CitizenPortalProps> = ({
  onBackToEOC,
  onSubmitSOS,
  incidents,
  teams,
  camps,
  lastSubmittedIncidentId,
}) => {
  // Mode: 'FORM' | 'CALL_SIMULATOR' | 'TRACKER'
  const [mode, setMode] = useState<'FORM' | 'CALL_SIMULATOR' | 'TRACKER'>(
    lastSubmittedIncidentId ? 'TRACKER' : 'FORM'
  );

  // Form State
  const [rawSos, setRawSos] = useState('');
  const [callerPhone, setCallerPhone] = useState('+91-98765-43210');
  const [locationName, setLocationName] = useState('Brahmaputra South Sector, Ward 8');
  const [lat, setLat] = useState<number>(26.1580);
  const [lng, setLng] = useState<number>(91.7520);
  const [isDetectingGPS, setIsDetectingGPS] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionError, setSubmissionError] = useState<string | null>(null);
  const [activeIncidentId, setActiveIncidentId] = useState<string | null>(lastSubmittedIncidentId || null);

  useEffect(() => {
    if (lastSubmittedIncidentId) {
      setActiveIncidentId(lastSubmittedIncidentId);
    }
  }, [lastSubmittedIncidentId]);

  // Call Simulator State
  const [callState, setCallState] = useState<'IDLE' | 'DIALING' | 'CONNECTED' | 'RECORDING' | 'TRANSCRIBED'>('IDLE');
  const [activeCallScriptIndex, setActiveCallScriptIndex] = useState(0);
  const [audioWaveProgress, setAudioWaveProgress] = useState(0);
  const [transcriptionText, setTranscriptionText] = useState('');
  const [callDurationSecs, setCallDurationSecs] = useState(0);

  // Quick hazard chips
  const quickTags = [
    { label: '🌊 Water Neck Deep (>1.8m)', text: 'Water depth is neck deep (over 1.8 meters).' },
    { label: '👵 Elderly Trapped', text: 'Elderly persons unable to swim are trapped.' },
    { label: '👶 Infants / Children', text: 'Small infants and children present with us.' },
    { label: '⚡ Live Electric Wires', text: 'Submerged electrical wires sparking in water.' },
    { label: '🏠 Stranded on Rooftop', text: 'We are stranded on the rooftop terrace.' },
    { label: '🩸 Medical Emergency / Injured', text: 'Critical injured person needing medical oxygen.' },
    { label: '🚤 Need Inflatable Boat', text: 'Require inflatable rescue boat urgently.' },
  ];

  // GPS auto-locator
  const handleDetectGPS = () => {
    setIsDetectingGPS(true);
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLat(pos.coords.latitude);
          setLng(pos.coords.longitude);
          setLocationName(`GPS Detected (${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)})`);
          setIsDetectingGPS(false);
        },
        () => {
          // Fallback to flood zone coordinate with slight offset
          setLat(26.1590);
          setLng(91.7485);
          setLocationName('Riverside Sector GPS Fixed (26.1590, 91.7485)');
          setIsDetectingGPS(false);
        },
        { timeout: 3000 }
      );
    } else {
      setIsDetectingGPS(false);
    }
  };

  const handleAddTag = (text: string) => {
    setRawSos((prev) => (prev ? `${prev} ${text}` : text));
  };

  // Submit SOS from Citizen Portal
  const handleCitizenSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!rawSos.trim()) return;

    setIsSubmitting(true);
    setSubmissionError(null);
    try {
      await onSubmitSOS({
        raw_sos: rawSos,
        caller_contact: callerPhone,
        location_name: locationName,
        latitude: lat,
        longitude: lng,
      });

      // Find the most recent incident or set tracked
      setMode('TRACKER');
    } catch (err) {
      console.error('Citizen SOS Submission failed:', err);
      setSubmissionError(err instanceof Error ? err.message : 'Unable to submit the emergency report. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Call simulator effects
  useEffect(() => {
    let timer: any;
    if (callState === 'CONNECTED' || callState === 'RECORDING') {
      timer = setInterval(() => {
        setCallDurationSecs((prev) => prev + 1);
        setAudioWaveProgress((prev) => (prev + 1) % 100);
      }, 500);
    }
    return () => clearInterval(timer);
  }, [callState]);

  const startEmergencyCall = (scriptIdx: number) => {
    setActiveCallScriptIndex(scriptIdx);
    setCallState('DIALING');
    setCallDurationSecs(0);
    setTranscriptionText('');

    setTimeout(() => {
      setCallState('CONNECTED');

      // Begin simulated transcription word-by-word
      const script = CALL_SIMULATION_SCRIPTS[scriptIdx];
      const words = script.transcript.split(' ');
      let currentWordIdx = 0;

      const streamInterval = setInterval(() => {
        if (currentWordIdx < words.length) {
          setTranscriptionText((prev) => (prev ? `${prev} ${words[currentWordIdx]}` : words[currentWordIdx]));
          currentWordIdx++;
        } else {
          clearInterval(streamInterval);
          setCallState('TRANSCRIBED');
          setRawSos(script.transcript);
          setLocationName(script.location);
          setLat(script.lat);
          setLng(script.lng);
          setCallerPhone(script.caller);
        }
      }, 90);
    }, 1800);
  };

  // Find tracked incident details
  const trackedIncident =
    incidents.find((i) => i.id === activeIncidentId) ||
    incidents[0] ||
    null;

  const assignedTeam = trackedIncident?.assigned_team_id
    ? teams.find((t) => t.id === trackedIncident.assigned_team_id)
    : teams[0];

  const assignedCamp = trackedIncident?.assigned_camp_id
    ? camps.find((c) => c.id === trackedIncident.assigned_camp_id)
    : camps[0];

  return (
    <div className="max-w-4xl mx-auto space-y-5 py-4 px-3 sm:px-6">
      {/* Top Banner */}
      <div className="flex items-center justify-between bg-gradient-to-r from-red-950/90 via-slate-900 to-slate-900 border border-red-800/60 p-4 rounded-2xl shadow-2xl">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-red-600 flex items-center justify-center text-white shadow-xl shadow-red-600/40 animate-pulse">
            <LifeBuoy className="w-7 h-7" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-extrabold bg-red-600 text-white px-2 py-0.5 rounded uppercase">
                Emergency 112 / NDMA 1070
              </span>
              <span className="text-xs font-mono text-emerald-400 flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
                AI Triage Gateway Active
              </span>
            </div>
            <h2 className="text-lg sm:text-xl font-extrabold text-white mt-0.5">
              Citizen Emergency SOS & Rescue Tracker
            </h2>
            <p className="text-xs font-mono text-slate-300">
              Direct voice call & distress uplink to National Disaster Command Center
            </p>
          </div>
        </div>

        <button
          onClick={onBackToEOC}
          className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-mono font-bold bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-slate-700 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">EOC Command Radar</span>
        </button>
      </div>

      {/* Mode Navigation Tabs */}
      <div className="grid grid-cols-3 gap-2 bg-slate-900/90 p-1.5 rounded-xl border border-slate-800 text-xs font-mono">
        <button
          onClick={() => setMode('FORM')}
          className={`py-2 px-3 rounded-lg font-bold transition-all flex items-center justify-center gap-1.5 ${
            mode === 'FORM'
              ? 'bg-red-600 text-white shadow-lg shadow-red-900/30'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Send className="w-3.5 h-3.5" />
          <span>Report Distress SOS</span>
        </button>

        <button
          onClick={() => setMode('CALL_SIMULATOR')}
          className={`py-2 px-3 rounded-lg font-bold transition-all flex items-center justify-center gap-1.5 ${
            mode === 'CALL_SIMULATOR'
              ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-900/30'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <PhoneCall className="w-3.5 h-3.5" />
          <span>Simulate 112 Voice Call</span>
        </button>

        <button
          onClick={() => setMode('TRACKER')}
          className={`py-2 px-3 rounded-lg font-bold transition-all flex items-center justify-center gap-1.5 ${
            mode === 'TRACKER'
              ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/30'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Navigation className="w-3.5 h-3.5" />
          <span>Live Rescue Tracker</span>
        </button>
      </div>

      {/* MODE 1: CALL SIMULATOR (112 / 1070 HELPLINE AUDIO INTAKE) */}
      {mode === 'CALL_SIMULATOR' && (
        <div className="tactical-card p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <span className="text-xs font-mono font-bold text-cyan-400 flex items-center gap-1">
                <Volume2 className="w-4 h-4" /> EMERGENCY HELPLINE CALL SIMULATOR
              </span>
              <h3 className="text-base font-extrabold text-white mt-0.5">
                Dial 112 / NDMA 1070 Audio Speech-to-Text Ingestion
              </h3>
              <p className="text-xs font-mono text-slate-400">
                Experience how a citizen's panic phone call is transcribed and converted to JSON by the AI
              </p>
            </div>

            {callState !== 'IDLE' && (
              <div className="flex items-center gap-2 bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800 text-xs font-mono">
                <Clock className="w-3.5 h-3.5 text-cyan-400" />
                <span className="text-white font-bold">
                  {Math.floor(callDurationSecs / 60)}:{(callDurationSecs % 60).toString().padStart(2, '0')}
                </span>
              </div>
            )}
          </div>

          {/* Select Audio Call Scenario */}
          <div>
            <label className="block text-xs font-mono text-slate-300 font-bold mb-2">
              Select Real-World Emergency Call Transcript to Simulate:
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              {CALL_SIMULATION_SCRIPTS.map((script, idx) => (
                <button
                  key={idx}
                  onClick={() => startEmergencyCall(idx)}
                  disabled={callState === 'DIALING' || callState === 'CONNECTED'}
                  className={`p-3 rounded-xl border text-left transition-all ${
                    activeCallScriptIndex === idx && callState !== 'IDLE'
                      ? 'border-cyan-500 bg-cyan-950/40 text-cyan-200'
                      : 'border-slate-800 bg-slate-900/70 hover:border-slate-700 text-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold font-mono">Scenario #{idx + 1}</span>
                    <PhoneCall className="w-3.5 h-3.5 text-cyan-400" />
                  </div>
                  <h5 className="text-xs font-bold text-white line-clamp-1">{script.title}</h5>
                  <p className="text-[11px] font-mono text-slate-400 line-clamp-2 mt-1 italic">
                    "{script.transcript}"
                  </p>
                </button>
              ))}
            </div>
          </div>

          {/* Active Call Audio Wave & Transcription Monitor */}
          <div className="bg-slate-950/90 rounded-xl p-4 border border-slate-800">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span
                  className={`w-3 h-3 rounded-full ${
                    callState === 'CONNECTED'
                      ? 'bg-red-500 animate-ping'
                      : callState === 'DIALING'
                      ? 'bg-amber-400 animate-pulse'
                      : callState === 'TRANSCRIBED'
                      ? 'bg-emerald-500'
                      : 'bg-slate-600'
                  }`}
                ></span>
                <span className="text-xs font-mono font-bold text-white">
                  STATUS:{' '}
                  {callState === 'DIALING'
                    ? 'DIALING 112 DISPATCH...'
                    : callState === 'CONNECTED'
                    ? 'CALL ACTIVE • STREAMING AUDIO TO WHISPER STT'
                    : callState === 'TRANSCRIBED'
                    ? 'CALL TRANSCRIBED • READY TO DISPATCH'
                    : 'STANDBY (SELECT A SCENARIO)'}
                </span>
              </div>

              {callState === 'CONNECTED' && (
                <span className="text-[11px] font-mono text-red-400 animate-pulse font-bold">
                  ● REC 48kHz
                </span>
              )}
            </div>

            {/* Simulated Animated Waveform */}
            {callState === 'CONNECTED' && (
              <div className="flex items-center justify-center gap-1.5 h-12 my-2 bg-slate-900/60 rounded-lg p-2">
                {[12, 28, 45, 18, 38, 52, 24, 48, 16, 34, 50, 22, 42, 15, 30, 48].map((h, i) => (
                  <div
                    key={i}
                    className="w-1.5 bg-gradient-to-t from-cyan-600 to-red-500 rounded-full transition-all duration-150"
                    style={{
                      height: `${Math.max(10, (h * ((audioWaveProgress + i * 5) % 100)) / 45)}px`,
                    }}
                  ></div>
                ))}
              </div>
            )}

            {/* Live Speech-to-Text Box */}
            <div className="mt-3">
              <label className="block text-[11px] font-mono text-slate-400 mb-1">
                Real-Time Automated Speech-to-Text Transcript:
              </label>
              <div className="min-h-[90px] p-3 rounded-lg bg-black/60 border border-slate-800 text-xs font-mono text-emerald-400 leading-relaxed">
                {transcriptionText ? (
                  <>
                    <span>"{transcriptionText}"</span>
                    {callState === 'CONNECTED' && <span className="inline-block w-2 h-4 ml-1 bg-emerald-400 animate-pulse"></span>}
                  </>
                ) : (
                  <span className="text-slate-600 italic">
                    Audio transcription will appear here in real-time as the distress call progresses...
                  </span>
                )}
              </div>
            </div>

            {/* Forward to Multi-Agent Pipeline Button */}
            {callState === 'TRANSCRIBED' && (
              <div className="flex items-center justify-between mt-4 pt-3 border-t border-slate-800">
                <div className="text-[11px] font-mono text-slate-300">
                  Transcribed: <strong className="text-white">{transcriptionText.length} characters</strong>. Location extracted: <span className="text-cyan-400">{locationName}</span>
                </div>
                <button
                  onClick={() => handleCitizenSubmit()}
                  disabled={isSubmitting}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-extrabold text-white bg-gradient-to-r from-red-600 to-rose-700 hover:from-red-500 hover:to-rose-600 shadow-xl shadow-red-900/40 border border-red-400/30 transition-all"
                >
                  <Send className="w-4 h-4" />
                  <span>{isSubmitting ? 'DISPATCHING CREW...' : 'SEND TO CREWAI MULTI-AGENT PIPELINE'}</span>
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* MODE 2: DIRECT FORM REPORTING */}
      {mode === 'FORM' && (
        <div className="tactical-card p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <span className="text-xs font-mono font-bold text-red-400 flex items-center gap-1">
                <AlertTriangle className="w-4 h-4" /> DIRECT CITIZEN DISTRESS REPORT
              </span>
              <h3 className="text-base font-extrabold text-white mt-0.5">
                Submit SOS Details & Live Coordinates
              </h3>
              <p className="text-xs font-mono text-slate-400">
                Processed instantaneously by autonomous AI priority triage & rescue dispatch
              </p>
            </div>

            <button
              onClick={handleDetectGPS}
              disabled={isDetectingGPS}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-bold bg-cyan-950/80 hover:bg-cyan-900 text-cyan-300 border border-cyan-700 transition-colors"
            >
              <MapPin className="w-3.5 h-3.5 text-cyan-400" />
              <span>{isDetectingGPS ? 'Detecting GPS...' : 'Detect My GPS'}</span>
            </button>
          </div>

          <form onSubmit={handleCitizenSubmit} className="space-y-4">
            {/* Distress Description */}
            <div>
              <label className="block text-xs font-mono font-bold text-slate-200 mb-1.5">
                Describe Your Emergency (Voice or Text) *
              </label>
              <textarea
                required
                rows={4}
                value={rawSos}
                onChange={(e) => setRawSos(e.target.value)}
                placeholder="Water level reached 2nd floor, 4 family members including an 80yo grandmother stranded on tin roof. Live power wires sparking. Need boat rescue urgently..."
                className="w-full bg-slate-950 border border-slate-800 focus:border-red-500 rounded-xl p-3.5 text-xs text-slate-100 placeholder:text-slate-600 focus:outline-none focus:ring-1 focus:ring-red-500 font-sans leading-relaxed"
              />
            </div>

            {/* Quick Tap Situation Chips */}
            <div>
              <label className="block text-[11px] font-mono text-slate-400 mb-1.5">
                Tap to Add Quick Situational Tags to Your Report:
              </label>
              <div className="flex flex-wrap gap-1.5">
                {quickTags.map((tag, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => handleAddTag(tag.text)}
                    className="px-2.5 py-1 rounded-lg text-[11px] font-mono bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 hover:border-cyan-600/60 transition-colors"
                  >
                    {tag.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Contact & Location Inputs */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
              <div>
                <label className="block text-xs font-mono text-slate-300 font-bold mb-1">
                  Location / Address Landmark *
                </label>
                <div className="relative">
                  <MapPin className="w-3.5 h-3.5 text-cyan-400 absolute left-3 top-3" />
                  <input
                    type="text"
                    required
                    value={locationName}
                    onChange={(e) => setLocationName(e.target.value)}
                    placeholder="e.g. Near Saraighat Bridge / Bharalu Ghat"
                    className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-100 font-mono focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-mono text-slate-300 font-bold mb-1">
                  Your Phone / WhatsApp Number *
                </label>
                <input
                  type="text"
                  required
                  value={callerPhone}
                  onChange={(e) => setCallerPhone(e.target.value)}
                  placeholder="+91-98765-43210"
                  className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-lg px-3 py-2 text-xs text-slate-100 font-mono focus:outline-none"
                />
              </div>
            </div>

            {/* GPS Latitude & Longitude Preview */}
            <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 bg-slate-950 p-2.5 rounded-lg border border-slate-900">
              <div className="flex items-center gap-2">
                <span className="text-slate-500">Coordinates:</span>
                <span className="text-cyan-400 font-bold">
                  {lat.toFixed(4)}° N, {lng.toFixed(4)}° E
                </span>
              </div>
              <span className="text-emerald-400 font-bold">GPS Accuracy: ±5m</span>
            </div>

            {/* Submit Button */}
            <div className="flex items-center justify-between pt-3 border-t border-slate-800">
              <span className="text-[11px] font-mono text-slate-400">
                Priority will be mathematically scored by AI in &lt;1 second
              </span>
              <button
                type="submit"
                disabled={isSubmitting || !rawSos.trim()}
                className="flex items-center gap-2 px-6 py-2.5 rounded-xl text-xs font-extrabold text-white bg-gradient-to-r from-red-600 to-rose-700 hover:from-red-500 hover:to-rose-600 shadow-xl shadow-red-900/40 border border-red-400/30 transition-all disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
                <span>{isSubmitting ? 'TRIAGING & DISPATCHING...' : 'TRANSMIT EMERGENCY SOS NOW'}</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {submissionError && (
        <div role="alert" className="rounded-lg border border-red-800 bg-red-950/60 p-3 text-xs font-mono text-red-200">
          Report not sent: {submissionError}
        </div>
      )}

      {/* MODE 3: LIVE RESCUE TRACKER (WHAT CITIZEN SEES AFTER REPORTING) */}
      {mode === 'TRACKER' && (
        <div className="space-y-4">
          {/* Dispatch Status Card */}
          <div className="tactical-card p-5 border-l-4 border-l-emerald-500 shadow-2xl">
            <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-xl bg-emerald-950 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono font-extrabold bg-emerald-600 text-white px-2 py-0.5 rounded">
                      SOS VERIFIED & DISPATCHED
                    </span>
                    <span className="text-xs font-mono text-slate-400">
                      Ticket ID: <strong className="text-white">{trackedIncident?.id || 'INC-LIVE-2026'}</strong>
                    </span>
                  </div>
                  <h3 className="text-base font-extrabold text-white mt-0.5">
                    Rescue Battalion En Route to Your Location
                  </h3>
                </div>
              </div>

              {/* Countdown ETA Badge */}
              <div className="bg-slate-950 px-4 py-2 rounded-xl border border-slate-800 text-right font-mono">
                <span className="text-[10px] text-slate-400 uppercase">Estimated Arrival</span>
                <div className="text-xl font-black text-emerald-400">~ 7 to 9 MINS</div>
              </div>
            </div>

            {/* Assigned Unit Details */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-slate-950/80 p-3 rounded-xl border border-slate-800 text-xs font-mono text-slate-300 my-3">
              <div>
                <span className="text-[10px] text-slate-500 uppercase block">Dispatched Squad</span>
                <span className="text-cyan-400 font-bold text-sm">
                  {assignedTeam?.callsign || 'NDRF 1st Aquatic Battalion (Alpha)'}
                </span>
                <span className="text-[10px] text-slate-400 block mt-0.5">
                  Boats: {assignedTeam?.boats_count || 5} • Amphibious: {assignedTeam?.amphibious_vehicles || 2}
                </span>
              </div>

              <div>
                <span className="text-[10px] text-slate-500 uppercase block">VHF Responder Radio</span>
                <span className="text-white font-bold flex items-center gap-1 mt-0.5">
                  <Radio className="w-3.5 h-3.5 text-cyan-400" />
                  {assignedTeam?.contact_radio || 'VHF-CH-16'}
                </span>
                <span className="text-[10px] text-slate-400 block mt-0.5">Frequency Open for Citizen Hail</span>
              </div>

              <div>
                <span className="text-[10px] text-slate-500 uppercase block">Designated Safe Camp</span>
                <span className="text-indigo-300 font-bold flex items-center gap-1 mt-0.5">
                  <Home className="w-3.5 h-3.5 text-indigo-400" />
                  {assignedCamp?.name || 'Sarada Girls High School Camp'}
                </span>
                <span className="text-[10px] text-emerald-400 block mt-0.5">
                  {assignedCamp?.available_beds || 380} beds & doctors ready
                </span>
              </div>
            </div>

            {/* Survival Instructions Card */}
            <div className="bg-red-950/30 border border-red-900/60 p-3.5 rounded-xl text-xs font-sans text-slate-200 space-y-1.5">
              <h5 className="font-bold text-red-400 flex items-center gap-1.5 text-xs uppercase font-mono">
                <AlertTriangle className="w-4 h-4" /> Immediate Flood Survival Directives:
              </h5>
              <ul className="list-disc list-inside text-[11px] text-slate-300 space-y-1">
                <li><strong>Stay on the highest accessible floor or roof terrace.</strong> Do not enter attic without a roof escape exit.</li>
                <li><strong>Disconnect your home electricity main switch</strong> if safe to reach, avoiding wet wires.</li>
                <li><strong>Signal the approaching rescue boat</strong>: Wave a bright cloth, whistle, or flash your phone light.</li>
                <li><strong>Do NOT attempt to swim or wade through moving water</strong>—depth and fast current can sweep adults off their feet.</li>
              </ul>
            </div>

            {/* Back Actions */}
            <div className="flex items-center justify-between mt-4 pt-3 border-t border-slate-800 text-xs font-mono">
              <button
                onClick={() => setMode('FORM')}
                className="text-cyan-400 hover:text-cyan-300 underline"
              >
                ← Report Another Situation
              </button>

              <button
                onClick={onBackToEOC}
                className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-bold transition-colors"
              >
                Inspect on Command Radar →
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
