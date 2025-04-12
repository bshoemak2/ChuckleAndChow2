import React from 'react';
import { View, Text, TextInput, TouchableOpacity, FlatList } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { styles } from './_styles';

interface FavoritesListProps {
  favorites: any[];
  setFavorites: (favorites: any[]) => void;
  search: string;
  setSearch: (search: string) => void;
  setSelectedFavorite: (favorite: any) => void;
}

export const FavoritesList: React.FC<FavoritesListProps> = ({
  favorites,
  setFavorites,
  search,
  setSearch,
  setSelectedFavorite,
}) => {
  const removeFavorite = async (title: string) => {
    if (confirm(`Remove ${title} from favorites?`)) {
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

  const renderFavorite = ({ item }) => (
    <View style={[styles.favItemContainer, { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', padding: 5 }]}>
      <TouchableOpacity onPress={() => onView(item)} style={{ flex: 1 }}>
        <Text style={[styles.favItem, { fontSize: 20, fontWeight: 'bold', color: '#000' }]}>
          🌟 {item.title}
        </Text>
      </TouchableOpacity>
      <TouchableOpacity
        style={{
          backgroundColor: '#FF3B30',
          paddingVertical: 5,
          paddingHorizontal: 10,
          borderRadius: 5,
        }}
        onPress={() => removeFavorite(item.title)}
      >
        <Text style={{ color: '#FFF', fontSize: 14 }}>Remove ❌</Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <View style={styles.favorites}>
      <Text style={styles.subtitle}>⭐ Favorites 💖</Text>
      <View style={styles.searchRow}>
        <TextInput
          style={[styles.input, { flex: 1 }]}
          placeholder="Search Favorites..."
          value={search}
          onChangeText={setSearch}
          placeholderTextColor="#A0A0A0"
        />
        <TouchableOpacity
          style={{ backgroundColor: '#FF3B30', padding: 10, borderRadius: 5 }}
          onPress={clearSearch}
        >
          <Text style={{ color: '#FFF', fontSize: 14 }}>✖</Text>
        </TouchableOpacity>
      </View>
      <FlatList
        data={filteredFavorites}
        keyExtractor={(item) => item.title}
        renderItem={renderFavorite}
        ListEmptyComponent={
          <Text style={styles.noFavorites}>No favorites found</Text>
        }
      />
    </View>
  );
};

export default FavoritesList;