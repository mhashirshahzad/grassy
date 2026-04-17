      - name: Move Inno script to root
        run: mv ./windows/grassy-installer.iss ./

      - name: Compile installer
        uses: Minionguyjpro/Inno-Setup-Action@v1.2.7
        with:
          path: grassy-installer.iss
