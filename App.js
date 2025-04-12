import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet } from 'react-native';

export default function App() {
  const [ingredients, setIngredients] = useState('');
  const [recipe, setRecipe] = useState(null);

  const fetchRecipe = async () => {
    try {
      const response = await fetch('http://localhost:5000/generate_recipe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ingredients: ingredients.split(',').map(item => item.trim()) }),
      });
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      console.log('Recipe received:', data); // Debug log
      setRecipe(data);
    } catch (error) {
      console.error('Fetch error:', error);
      alert('Failed to fetch recipe');
    }
  };

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        placeholder="Enter ingredients (e.g., chicken, rice)"
        value={ingredients}
        onChangeText={setIngredients}
      />
      <Button title="Generate Recipe" onPress={fetchRecipe} />
      {recipe && (
        <View>
          <Text style={styles.title}>{recipe.title}</Text>
          <Text>Steps: {recipe.steps.join(' ')}</Text>
          <Text>Calories: {recipe.nutrition.calories}</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, justifyContent: 'center' },
  input: { borderWidth: 1, padding: 10, marginBottom: 10 },
  title: { fontSize: 20, fontWeight: 'bold' },
});