import React, { useState } from 'react';
import { SafeAreaView, View, Text, TextInput, Button, StyleSheet, Alert } from 'react-native';

// development backend - set to your machine IP when testing on a real device
const BACKEND = 'http://localhost:8000'; // or 'http://10.0.2.2:8000' for Android emulator
const AUTH_TOKEN = 'dev-token-CHANGE';

export default function App(){
  const [patientId, setPatientId] = useState('1');
  const [symptoms, setSymptoms] = useState('');
  const [triageResult, setTriageResult] = useState(null);
  const [scheduleAt, setScheduleAt] = useState(new Date().toISOString().slice(0,19));
  const [notes, setNotes] = useState('');

  async function doTriage(){
    try{
      const res = await fetch(`${BACKEND}/triage_chain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${AUTH_TOKEN}` },
        body: JSON.stringify({ patient_id: Number(patientId), symptoms })
      });
      const j = await res.json();
      setTriageResult(j.triage || JSON.stringify(j));
    }catch(e){ Alert.alert('Error', String(e)); }
  }

  async function doSchedule(){
    try{
      const res = await fetch(`${BACKEND}/schedule`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${AUTH_TOKEN}` },
        body: JSON.stringify({ patient_id: Number(patientId), scheduled_at: scheduleAt, notes })
      });
      const j = await res.json();
      Alert.alert('Scheduled', JSON.stringify(j));
    }catch(e){ Alert.alert('Error', String(e)); }
  }

  async function lookupRx(){
    try{
      const res = await fetch(`${BACKEND}/prescription/${patientId}`, { headers: { 'Authorization': `Bearer ${AUTH_TOKEN}` }});
      const j = await res.json();
      Alert.alert('Prescription', JSON.stringify(j));
    }catch(e){ Alert.alert('Error', String(e)); }
  }

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.h1}>Healthcare Virtual Assistant — Demo</Text>
      <Text>Patient ID</Text>
      <TextInput style={styles.input} value={patientId} onChangeText={setPatientId} keyboardType="numeric" />

      <Text style={{marginTop:10}}>Symptom Triage</Text>
      <TextInput style={styles.input} value={symptoms} onChangeText={setSymptoms} placeholder="Describe symptoms" />
      <Button title="Run Triage" onPress={doTriage} />
      {triageResult ? (<View style={{marginTop:8}}><Text>Result:</Text><Text>{triageResult}</Text></View>) : null}

      <View style={{height:1, backgroundColor:'#eee', marginVertical:12}} />

      <Text>Schedule (ISO)</Text>
      <TextInput style={styles.input} value={scheduleAt} onChangeText={setScheduleAt} />
      <TextInput style={styles.input} value={notes} onChangeText={setNotes} placeholder="Notes" />
      <Button title="Schedule" onPress={doSchedule} />

      <View style={{height:1, backgroundColor:'#eee', marginVertical:12}} />
      <Button title="Lookup Latest Prescription" onPress={lookupRx} />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#fff' },
  h1: { fontSize: 18, fontWeight: '700', marginBottom: 12 },
  input: { borderWidth: 1, borderColor: '#ccc', padding: 8, marginVertical: 6, borderRadius: 6 }
});
