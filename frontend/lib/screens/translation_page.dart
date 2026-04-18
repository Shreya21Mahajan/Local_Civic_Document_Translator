import 'package:flutter/material.dart';
import 'package:just_audio/just_audio.dart';

class TranslationPage extends StatefulWidget {
  final List<String> lines;
  final List<String> audioFiles;

  const TranslationPage({
    super.key,
    required this.lines,
    required this.audioFiles,
  });

  @override
  _TranslationPageState createState() => _TranslationPageState();
}

class _TranslationPageState extends State<TranslationPage> {
  final AudioPlayer player = AudioPlayer();

  Future<void> playSequential() async {
    for (var file in widget.audioFiles) {
      await player.setUrl("http://10.0.2.2:5000/audio/$file");
      await player.play();

      await player.playerStateStream.firstWhere(
        (state) => state.processingState == ProcessingState.completed,
      );
    }
  }

  @override
  void dispose() {
    player.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Translation Result")),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              itemCount: widget.lines.length,
              itemBuilder: (context, index) {
                return ListTile(
                  title: Text(widget.lines[index]),
                );
              },
            ),
          ),
          ElevatedButton(
            onPressed: playSequential,
            child: const Text("Play Audio"),
          ),
        ],
      ),
    );
  }
}
