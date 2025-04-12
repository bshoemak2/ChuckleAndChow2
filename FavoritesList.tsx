// app/FavoritesList.tsx
import React from 'react';
import { View, Text, TextInput, Button } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { styles } from './_styles';

interface FavoritesListProps {
  favorites: any[];
  setFavorites: (favorites: any[]) => void;
  language: string;
  search: string;
  setSearch: (search: string) => void;
  setSelectedFavorite: (favorite: any) => void;
}

export const FavoritesList: React.FC<FavoritesListProps> = ({
  favorites,
  setFavorites,
  language,
  search,
  setSearch,
  setSelectedFavorite,
}) => {
  const removeFavorite = async (title: string) => {
    if (confirm(language === 'english' ? `Remove ${title} from favorites?` : `¿Eliminar ${title} de favoritos?`)) {
      const newFavorites = favorites.filter(fav => fav.title !== title);
      setFavorites(newFavorites);
      try {
        await AsyncStorage.setItem('favorites', JSON.stringify(newFavorites));
      } catch (error) {
        console.error('Error removing favorite:', error);
      }
      setSelectedFavorite(null);
    }
  };

  const onView = (fav) => setSelectedFavorite(fav);

  const clearSearch = () => setSearch('');

  const filteredFavorites = favorites.filter(fav => fav.title.toLowerCase().includes(search.toLowerCase()));

  return (
    <View style={styles.favorites}>
      <Text style={styles.subtitle}>⭐ {language === 'english' ? 'Favorites 💖' : 'Favoritos 💖'}</Text>
      <View style={styles.searchRow}>
        <TextInput
          style={[styles.input, { flex: 1 }]}
          placeholder={language === 'english' ? 'Search favorites...' : 'Buscar favoritos...'}
          value={search}
          onChangeText={setSearch}
          placeholderTextColor="#A0A0A0"
        />
        <Button title="✖" onPress={clearSearch} color="#FF3B30" />
      </View>
      {filteredFavorites.length > 0 ? (
        filteredFavorites.map((fav, index) => (
          <View key={index} style={styles.favItemContainer}>
            <Text style={styles.favItem} onPress={() => onView(fav)}>
              🌟 {fav.title}
            </Text>
            <Button
              title={language === 'english' ? "Remove ❌" : "Eliminar ❌"}
              onPress={() => removeFavorite(fav.title)}
              color="#FF3B30"
            />
          </View>
        ))
      ) : (
        <Text style={styles.noFavorites}>
          {language === 'english' ? 'No favorites found' : 'No se encontraron favoritos'}
        </Text>
      )}
    </View>
  );
};

export default FavoritesList;