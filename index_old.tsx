// app/index.tsx
import React, { useState, useEffect } from 'react';
import {
  ScrollView,
  View,
  Text,
  Button,
  StyleSheet,
  ActivityIndicator,
  Platform,
  Share,
  Linking,
  Image,
  TouchableOpacity,
  Picker,
} from 'react-native';
import Animated, { Easing, FadeIn, FadeInUp } from 'react-native-reanimated';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Link } from 'expo-router';
import { FavoritesList } from './FavoritesList';
import { styles } from './_styles';
import * as Clipboard from 'expo-clipboard';

const AnimatedView = Platform.OS === 'web' ? View : Animated.View;

export default function HomeScreen() {
  const [meat, setMeat] = useState('');
  const [vegetable, setVegetable] = useState('');
  const [fruit, setFruit] = useState('');
  const [seafood, setSeafood] = useState('');
  const [dairy, setDairy] = useState('');
  const [carb, setCarb] = useState('');
  const [devilWater, setDevilWater] = useState('');
  const [style, setStyle] = useState('');
  const [category, setCategory] = useState('');
  const [language, setLanguage] = useState('english');
  const [recipe, setRecipe] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [favorites, setFavorites] = useState([]);
  const [lastRandom, setLastRandom] = useState(false);
  const [showFavorites, setShowFavorites] = useState(false);
  const [selectedFavorite, setSelectedFavorite] = useState(null);
  const [search, setSearch] = useState('');
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState(null);

  const API_URL = 'http://localhost:5000';

  const INGREDIENT_CATEGORIES = {
    meat: [
      { name: 'ground beef', emoji: '🍔' },
      { name: 'chicken', emoji: '🍗' },
      { name: 'pork', emoji: '🥓' },
      { name: 'lamb', emoji: '🐑' },
      { name: 'pichana', emoji: '🥩' },
      { name: 'churrasco', emoji: '🍖' },
      { name: 'ribeye steaks', emoji: '🍽️' },
      { name: 'squirrel', emoji: '🐿️' },
      { name: 'rabbit', emoji: '🐰' },
      { name: 'quail', emoji: '🐦' },
      { name: 'woodpecker', emoji: '🦜' },
    ],
    vegetables: [
      { name: 'carrot', emoji: '🥕' },
      { name: 'broccoli', emoji: '🥦' },
      { name: 'onion', emoji: '🧅' },
      { name: 'potato', emoji: '🥔' },
      { name: 'tomato', emoji: '🍅' },
      { name: 'green beans', emoji: '🌱' },
      { name: 'okra', emoji: '🌿' },
      { name: 'collards', emoji: '🥬' },
    ],
    fruits: [
      { name: 'apple', emoji: '🍎' },
      { name: 'banana', emoji: '🍌' },
      { name: 'lemon', emoji: '🍋' },
      { name: 'orange', emoji: '🍊' },
      { name: 'mango', emoji: '🥭' },
      { name: 'avocado', emoji: '🥑' },
      { name: 'starfruit', emoji: '✨' },
      { name: 'dragon fruit', emoji: '🐉' },
      { name: 'carambola', emoji: '🌟' },
    ],
    seafood: [
      { name: 'salmon', emoji: '🐟' },
      { name: 'shrimp', emoji: '🦐' },
      { name: 'cod', emoji: '🐠' },
      { name: 'tuna', emoji: '🐡' },
      { name: 'yellowtail snapper', emoji: '🎣' },
      { name: 'grouper', emoji: '🪸' },
      { name: 'red snapper', emoji: '🌊' },
      { name: 'oysters', emoji: '🦪' },
      { name: 'lobster', emoji: '🦞' },
      { name: 'conch', emoji: '🐚' },
      { name: 'lionfish', emoji: '🦈' },
      { name: 'catfish', emoji: '🐺' },
      { name: 'bass', emoji: '🎸' },
      { name: 'crappie', emoji: '🐳' },
    ],
    dairy: [
      { name: 'cheese', emoji: '🧀' },
      { name: 'milk', emoji: '🥛' },
      { name: 'butter', emoji: '🧈' },
      { name: 'yogurt', emoji: '🍶' },
      { name: 'eggs', emoji: '🥚' },
    ],
    carbs: [
      { name: 'bread', emoji: '🍞' },
      { name: 'pasta', emoji: '🍝' },
      { name: 'rice', emoji: '🍚' },
      { name: 'tortilla', emoji: '🌮' },
    ],
    devilWater: [
      { name: 'beer', emoji: '🍺' },
      { name: 'moonshine', emoji: '🥃' },
      { name: 'whiskey', emoji: '🥃' },
      { name: 'vodka', emoji: '🍸' },
      { name: 'tequila', emoji: '🌵' },
    ],
  };

  const AFFILIATE_LINKS = [
    {
      title: '🍔 Bubba’s Burger Smasher 🍔',
      url: 'https://amzn.to/4jwsA8w',
      image: 'https://m.media-amazon.com/images/I/61msHBPisBL._AC_SX425_.jpg',
    },
    {
      title: '🥃 Hillbilly Moonshine Maker 🥃',
      url: 'https://amzn.to/4lwVxmw',
      image: 'https://m.media-amazon.com/images/I/418WMdO5DQS._AC_US100_.jpg',
    },
    {
      title: '🔪 Granny’s Hog-Slicin’ Knife 🔪',
      url: 'https://amzn.to/4lp4j5M',
      image: 'https://m.media-amazon.com/images/I/61p28HGfcGL._AC_SY450_.jpg',
    },
    {
      title: '🍺 Redneck Beer Pong Kit 🍺',
      url: 'https://amzn.to/42re7n7',
      image: 'https://m.media-amazon.com/images/I/81ZrDViTBTL._AC_SY355_.jpg',
    },
  ];

  useEffect(() => {
    const loadFavorites = async () => {
      try {
        const saved = await AsyncStorage.getItem('favorites');
        if (saved) setFavorites(JSON.parse(saved));
      } catch (error) {
        console.error('Error loading favorites—blame the possum:', error);
      }
    };
    loadFavorites();
  }, []);

  const fetchRecipe = async (isRandom = false) => {
    const selectedIngredients = [meat, vegetable, fruit, seafood, dairy, carb, devilWater].filter(Boolean);
    if (!selectedIngredients.length && !isRandom) {
      setRecipe({ title: "Error 🤦‍♂️", steps: ["Pick somethin’, ya lazy bum! 😛"], nutrition: { calories: 0 } });
      setError(null);
      setIsLoading(false);
      setLastRandom(isRandom);
      return;
    }
    setIsLoading(true);
    setRecipe(null);
    setError(null);
    setLastRandom(isRandom);
    const url = `${API_URL}/generate_recipe`;
    const requestBody = JSON.stringify({
      ingredients: selectedIngredients,
      preferences: { style, category, language, isRandom },
    });
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: requestBody,
      });
      if (!response.ok) throw new Error(`API farted: ${response.status} 💨`);
      const data = await response.json();
      console.log('Fetched recipe:', data);
      setRecipe(data);
    } catch (error) {
      setError(error.message);
      setRecipe({ title: "Epic Fail 🚨", steps: [`Cookin’ crashed: ${error.message} 🤡`], nutrition: { calories: 0 } });
    } finally {
      setIsLoading(false);
    }
  };

  const saveFavorite = async () => {
    if (recipe && !favorites.some((fav) => fav.title === recipe.title)) {
      const newFavorites = [...favorites, recipe];
      setFavorites(newFavorites);
      try {
        await AsyncStorage.setItem('favorites', JSON.stringify(newFavorites));
      } catch (error) {
        console.error('Error hoardin’ yer stash:', error);
      }
    }
  };

  const shareRecipe = async (platform = 'default') => {
    const currentRecipe = selectedFavorite || recipe;
    if (!currentRecipe) return;
    const shareText = currentRecipe.shareText || `${currentRecipe.title}\n${currentRecipe.ingredients.join('\n')}\n${currentRecipe.steps.join('\n')}`;
    const url = 'https://recipegenerator-frontend.onrender.com/';
    const fullMessage = `Get a load of this hogwash: ${shareText}\nCheck out my app: ${url} 🤠`;
    try {
      if (platform === 'default' || platform === 'more') {
        await Share.share({ message: fullMessage });
      } else if (platform === 'twitter') {
        const tweetUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(fullMessage)}`;
        await Linking.openURL(tweetUrl);
      } else if (platform === 'facebook') {
        const fbUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}&quote=${encodeURIComponent(shareText)}`;
        await Linking.openURL(fbUrl);
      }
    } catch (error) {
      console.error('Share flopped—too spicy for the interwebs:', error);
      setError('Failed to share—check yer signal!');
    }
  };

  const copyToClipboard = async () => {
    const currentRecipe = selectedFavorite || recipe;
    if (!currentRecipe) return;
    const textToCopy = `${currentRecipe.title}\n\nIngredients:\n${currentRecipe.ingredients.join('\n')}\n\nSteps:\n${currentRecipe.steps.join('\n')}`;
    try {
      await Clipboard.setStringAsync(textToCopy);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Clipboard error—fingers too greasy:', error);
      setError('Clipboard snag—try again!');
    }
  };

  const toggleLanguage = () => {
    const newLanguage = language === 'english' ? 'spanish' : 'english';
    setLanguage(newLanguage);
    if (meat || vegetable || fruit || seafood || dairy || carb || devilWater || recipe) fetchRecipe(lastRandom);
  };

  const clearInput = () => {
    setMeat('');
    setVegetable('');
    setFruit('');
    setSeafood('');
    setDairy('');
    setCarb('');
    setDevilWater('');
    setStyle('');
    setCategory('');
    setRecipe(null);
    setError(null);
    setLastRandom(false);
    setSelectedFavorite(null);
    setSearch('');
  };

  const fetchRandomRecipe = () => fetchRecipe(true);

  const toggleFavorites = () => {
    setShowFavorites(!showFavorites);
    setSelectedFavorite(null);
    setSearch('');
  };

  const AffiliateSection = () => (
    <View style={styles.affiliateSection}>
      <Text style={styles.affiliateHeader}>💰 Git Yer Loot Here, Y’all! 💸</Text>
      {AFFILIATE_LINKS.map((link) => (
        <TouchableOpacity key={link.title} style={styles.affiliateButton} onPress={() => Linking.openURL(link.url)}>
          <Image
            source={{ uri: link.image }}
            style={styles.affiliateImage}
            onError={(e) => console.error(`Image failed to load: ${link.image}, error: ${e.nativeEvent.error}`)}
            defaultSource={require('../assets/fallback.png')}
          />
          <Text style={styles.affiliateText}>{link.title}</Text>
        </TouchableOpacity>
      ))}
      <Text style={styles.affiliateDisclaimer}>As an Amazon Associate, I earn from qualifyin’ purchases, yeehaw!</Text>
    </View>
  );

  const RecipeCard = ({ recipe, language, onShare, onSave, onBack }) => {
    console.log('Rendering RecipeCard with:', recipe);
    return (
      <View style={styles.recipeCard}>
        <Text style={styles.recipeTitle}>{recipe.title || 'No Title'}</Text>
        <Text style={styles.recipeSection}>Ingredients:</Text>
        {(recipe.ingredients || []).map((ing, i) => (
          <Text key={i} style={styles.recipeText}>
            - {ing}
          </Text>
        ))}
        <Text style={styles.recipeSection}>Steps:</Text>
        {(recipe.steps || []).map((step, i) => (
          <Text key={i} style={styles.recipeText}>
            {i + 1}. {step}
          </Text>
        ))}
        <Text style={styles.recipeSection}>Nutrition:</Text>
        <Text style={styles.recipeText}>
          Calories: {recipe.nutrition?.calories || 0} (Chaos: {recipe.nutrition?.chaos_factor || 0}/10)
        </Text>
        <Text style={styles.recipeSection}>Gear:</Text>
        <Text style={styles.recipeText}>{(recipe.equipment || []).join(', ') || 'None'}</Text>
        <View style={styles.recipeActions}>
          <TouchableOpacity
            style={[styles.copyButton, { backgroundColor: copied ? '#4ECDC4' : '#FF69B4', borderColor: '#FFD700' }]}
            onPress={copyToClipboard}
          >
            <Text style={[styles.copyButtonText, { color: '#FFF' }]}>{copied ? 'Snagged It! 🎯' : 'Copy to Clipboard 📋'}</Text>
          </TouchableOpacity>
          <Button title="🐦 Share to X" onPress={() => onShare('twitter')} color="#1DA1F2" />
          <Button title="📘 Share to Facebook" onPress={() => onShare('facebook')} color="#4267B2" />
          <Button title="📣 Share to Pals" onPress={() => onShare('default')} color="#FF6B6B" />
          {onSave && <Button title="💾 Hoard This Gem" onPress={onSave} color="#4ECDC4" />}
          {onBack && <Button title="⬅️ Back to the Heap" onPress={onBack} color="#FFD93D" />}
        </View>
      </View>
    );
  };

  const PickerSection = ({ label, category, value, onValueChange, bgColor, borderColor }) => (
    <View style={styles.inputSection}>
      <Text style={[styles.inputLabel, { backgroundColor: bgColor, color: '#FFD700' }]}>{label}</Text>
      <Picker selectedValue={value} onValueChange={onValueChange} style={[styles.picker, { backgroundColor: bgColor, borderColor }]}>
        <Picker.Item label="None" value="" color="#FFF" />
        {INGREDIENT_CATEGORIES[category].map((item) => (
          <Picker.Item key={item.name} label={`${item.name} ${item.emoji}`} value={item.name} color="#FFF" />
        ))}
      </Picker>
    </View>
  );

  console.log('Rendering HomeScreen, recipe:', recipe);

  return (
    <ScrollView style={styles.scrollContainer} contentContainerStyle={styles.scrollContent}>
      <AnimatedView entering={Platform.OS !== 'web' ? FadeIn.duration(800).easing(Easing.out(Easing.exp)) : undefined} style={styles.container}>
        <Text style={styles.header}>🤪 Chuckle & Chow: Recipe Rumble 🍔💥</Text>
        <Text style={styles.subheader}>Cookin’ Up Chaos for Rednecks, Rebels, and Rascals! 🎸🔥</Text>
        <View style={styles.trustSection}>
          <Text style={styles.trustText}>🌶️ Hotter than a jalapeño’s armpit</Text>
          <Text style={styles.trustText}>🍺 Best with a cold one, yeehaw!</Text>
          <Text style={styles.trustText}>🐷 Crazier than a hog on a hot tin roof</Text>
        </View>
        <PickerSection label="🥩 Meaty Madness 🍖" category="meat" value={meat} onValueChange={setMeat} bgColor="#FF6347" borderColor="#FFD700" />
        <PickerSection
          label="🥕 Veggie Voodoo 🥔"
          category="vegetables"
          value={vegetable}
          onValueChange={setVegetable}
          bgColor="#228B22"
          borderColor="#ADFF2F"
        />
        <PickerSection
          label="🍎 Fruity Frenzy 🍋"
          category="fruits"
          value={fruit}
          onValueChange={setFruit}
          bgColor="#FF1493"
          borderColor="#FFB6C1"
        />
        <PickerSection
          label="🦐 Sea Critter Chaos 🐟"
          category="seafood"
          value={seafood}
          onValueChange={setSeafood}
          bgColor="#20B2AA"
          borderColor="#00FFFF"
        />
        <PickerSection label="🧀 Dairy Delirium 🧀" category="dairy" value={dairy} onValueChange={setDairy} bgColor="#FFA500" borderColor="#FFD700" />
        <PickerSection label="🍞 Carb Craze 🍝" category="carbs" value={carb} onValueChange={setCarb} bgColor="#8B4513" borderColor="#FFD700" />
        <PickerSection
          label="🥃 Devil Water Disaster 🍺"
          category="devilWater"
          value={devilWater}
          onValueChange={setDevilWater}
          bgColor="#800080"
          borderColor="#FFD700"
        />
        {isLoading && (
          <View style={styles.spinnerContainer}>
            <ActivityIndicator size="large" color="#FF6B6B" />
            <Text style={[styles.spinnerText, { color: '#FF1493', fontWeight: 'bold' }]}>
              🔥 Whippin’ up somethin’ nuttier than squirrel turds... 🐿️
            </Text>
          </View>
        )}
        {error && (
          <Text style={[styles.error, { color: '#FF1493', fontSize: 20, marginVertical: 10 }]}>💥 Dang it! {error} 🤦‍♂️</Text>
        )}
        <AnimatedView entering={Platform.OS !== 'web' ? FadeInUp.delay(600).duration(600) : undefined} style={styles.buttonRow}>
          <Button title="🍳 Cook Me a Hoot! 🎉" onPress={() => fetchRecipe(false)} disabled={isLoading} color="#FF4500" />
          <Button title="🎲 Random Ruckus Recipe 🌩️" onPress={fetchRandomRecipe} disabled={isLoading} color="#FF00A0" />
          <Button title="🧹 Wipe the Slate, Bubba 🐴" onPress={clearInput} color="#4ECDC4" />
          <Button
            title={language === 'english' ? '🌮 Speak Español, Amigo' : '🇺🇸 Back to ‘Merican'}
            onPress={toggleLanguage}
            color="#FFD93D"
          />
          <Button title={showFavorites ? '🙈 Hide My Stash' : '💰 Show My Stash'} onPress={toggleFavorites} color="#4ECDC4" />
        </AnimatedView>
        {recipe && recipe.title !== 'Error' && !selectedFavorite && (
          <RecipeCard recipe={recipe} language={language} onShare={shareRecipe} onSave={saveFavorite} />
        )}
        {recipe && recipe.title === 'Error' && (
          <AnimatedView entering={Platform.OS !== 'web' ? FadeIn.duration(800) : undefined} style={styles.errorContainer}>
            <Text style={[styles.error, { color: '#FF1493', fontSize: 20 }]}>💥 Dang it! {recipe.steps[0]} 🤦‍♂️</Text>
            <Button title="🐴 Retry, Ya Mule!" onPress={() => fetchRecipe(lastRandom)} color="#FF3D00" />
          </AnimatedView>
        )}
        {showFavorites && favorites.length > 0 && (
          <FavoritesList
            favorites={favorites}
            setFavorites={setFavorites}
            language={language}
            search={search}
            setSearch={setSearch}
            setSelectedFavorite={setSelectedFavorite}
          />
        )}
        {selectedFavorite && (
          <RecipeCard recipe={selectedFavorite} language={language} onShare={shareRecipe} onBack={() => setSelectedFavorite(null)} />
        )}
        <AffiliateSection />
        <View style={[styles.footer, { backgroundColor: '#FFD700', borderTopWidth: 3, borderTopColor: '#FF4500' }]}>
          <Image
            source={require('../assets/gt.png')}
            style={{ width: 80, height: 80, marginRight: 10, borderWidth: 2, borderColor: '#FF00A0' }}
          />
          <Text style={[styles.footerText, { color: '#FF4500', fontWeight: 'bold' }]}>© 2025 Chuckle & Chow 🌟</Text>
          <Text style={[styles.footerText, { color: '#FF4500', fontWeight: 'bold' }]}>
            <Link href="/privacy-policy" style={[styles.footerLink, { color: '#FF00A0' }]}>
              Privacy Policy (Y’all Ain’t Sneaky Enough) 🕵️‍♂️
            </Link>
          </Text>
          <Text style={[styles.footerText, { color: '#FF4500', fontWeight: 'bold' }]}>
            For issues and hollerin’, hit us at{' '}
            <Text style={[styles.footerLink, { color: '#FF00A0' }]} onPress={() => Linking.openURL('mailto:bshoemak@mac.com')}>
              bshoemak@mac.com 📧
            </Text>
          </Text>
        </View>
      </AnimatedView>
    </ScrollView>
  );
}